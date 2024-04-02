"""
Created on 25.11.2022

@author: wf
"""
from typing import Callable, List
from nicegui import ui
from ngwidgets.webserver import WebSolution
from ngwidgets.widgets import HideShow, Link
from meta.metamodel import Context

from yprinciple.target import Target
from yprinciple.ypcell import YpCell

class GeneratorGrid:
    """
    generator and selection grid

    see https://wiki.bitplan.com/index.php/Y-Prinzip#Example
    """

    def __init__(self, targets: dict, parent, solution:WebSolution, iconSize: str = "32px"):
        """
        constructor

        Args:
            targets(dict): a list of targets
            parent: the parent element
            solution(WebSolution): the solution

        """
        self.parent = parent
        self.solution = solution
        self.color_schema = solution.config.color_schema
        self.iconSize = iconSize
        self.checkboxes = {}
        self.ypcell_by_id = {}
        self.checkbox_by_id = {}
        self.header_checkbox_by_id = {}
        self.cell_debug_msg_divs = []
        self.targets = targets
        self.setup_ui()
        
    def setup_styles(self):
        """
        setup the styles for the ui
        """
        self.header_classes = "text-center"
        # centering
        self.center_classes = "flex flex-col items-center justify-center"
        # see https://www.materialpalette.com/indigo/indigo
        # and https://github.com/WolfgangFahl/nicegui_widgets/blob/main/ngwidgets/color_schema.py
        # light primary color
        self.header_background = "#c5cae9"
        # 
        self.light_header_background = "#f5f5f5"
        self.bs_secondary = "#6c757d"
        self.header_style = (
            f"font-size: 1.0rem;background-color: {self.header_background}"
        )
        self.light_header_style = f"background-color: {self.light_header_background}"
        
    def setup_target_header_row(self):
        """
        setup the header row
        """
        with self.grid:
            self.generateButton = ui.button(
                icon="play_circle",
                on_click=self.onGenerateButtonClick
            )
            self.targets_column_header = ui.html().classes(self.header_classes).style(self.header_style)
            self.targets_column_header.content = "<strong>Target</strong>"
            for target in self.displayTargets():
                classes=self.header_classes+self.center_classes
                target_header_cell=ui.row().classes(classes).style(self.header_style)
                with target_header_cell:
                    target_header_div=ui.html()
                    markup=f"<span style='align-middle'><strong>{target.name}</strong><br></span>"
                    #<i class="mdi mdi-archive" style="color: rgb(108, 117, 125); font-size: 32px;"></i>
                    #markup+=f"""<i class="mdi mdi-{target.icon_name}" style="color: {self.bs_secondary};font-size:{self.iconSize};"></i>"""
                    #<i class="q-icon notranslate material-icons" aria-hidden="true" role="presentation" id="c48">archive</i>
                    ui.icon(target.icon_name,size=self.iconSize,color=self.bs_secondary)
                    #markup+=f"""<i class="q-icon notranslate material-icons" aria-hidden="true" role="presentation">{target.icon_name}</i>"""
                    target_header_div.content=markup
                    pass
                
    def setup_topic_header_row(self):
        """
        setup the second header row
        """
        with self.grid:
            self.topics_column_header = ui.html().classes(self.header_classes).style(self.header_style)
            self.topics_column_header.content = "<strong>Topics</strong>"
        self.header_checkboxes={}
        self.header_checkboxes["all"]=self.create_simple_checkbox(
            parent=self.grid,
            label_text="↘",
            title="select all",
            classes=self.center_classes,
            on_change=self.onSelectAllClick,
        )
        for target in self.displayTargets():
            self.header_checkboxes[target.name]=self.create_simple_checkbox(
                parent=self.grid,
                label_text="↓",
                title=f"select all {target.name}",
                classes=self.center_classes,
                on_change=self.onSelectColumnClick,
            )
       
    def setup_ui(self):
        """
        setup the user interface
        """
        self.setup_styles()
        with self.parent:
            target_columns=len(self.displayTargets())
            # two more for the Topics and check box columns
            target_columns+=2
            self.grid = ui.grid(columns=target_columns).classes('w-full gap-0')
            self.setup_target_header_row()
            self.setup_topic_header_row()

    def getCheckedYpCells(self) -> List[YpCell]:
        """
        get all checked YpCells
        """
        checkedYpCells = []
        # generate in order of rows
        for checkbox_row in self.checkboxes.values():
            for checkbox, ypCell in checkbox_row.values():
                if checkbox.isChecked():
                    checkedYpCells.append(ypCell)
                for subCell in ypCell.subCells.values():
                    checkbox = self.checkbox_by_id[subCell.checkbox_id]
                    if checkbox.isChecked():
                        checkedYpCells.append(subCell)
        return checkedYpCells

    async def onGenerateButtonClick(self, _msg):
        """
        react on the generate button having been clicked
        """
        # force login
        self.solution.smwAccess.wikiClient.login()
        cellsToGen = self.getCheckedYpCells()
        for ypCell in cellsToGen:
            cell_checkbox = self.checkbox_by_id.get(ypCell.checkbox_id, None)
            status_div = cell_checkbox.status_div
            status_div.delete_components()
            status_div.text = ""
            try:
                genResult = ypCell.generateViaMwApi(
                    smwAccess=self.solution.smwAccess,
                    dryRun=self.solution.dryRun,
                    withEditor=self.solution.openEditor,
                )
                if genResult is not None and cell_checkbox is not None:
                    delta_color = ""
                    diff_url = genResult.getDiffUrl()
                    if diff_url is not None:
                        if genResult.page_changed():
                            delta_color = "text-red-500"
                        else:
                            delta_color = "text-green-500"
                    else:
                        delta_color = "text-gray-500"
                    with status_div:
                        link=Link.create(url=diff_url, text="Δ")
                        _link_html=ui.html(link).classes("text-xl font-bold " + delta_color,)
            except BaseException as ex:
                with status_div:
                    ui.label("❗").tooltip(str(ex))
                self.solution.handle_exception(ex)

    def check_ypcell_box(self, checkbox, ypCell, checked: bool):
        """
        check the given checkbox and the ypCell belonging to it
        """
        checkbox.check(checked)
        self.checkSubCells(ypCell, checked)

    def checkSubCells(self, ypCell, checked):
        # loop over all subcells
        for subcell in ypCell.subCells.values():
            # and set the checkbox value accordingly
            checkbox = self.checkbox_by_id[subcell.checkbox_id]
            checkbox.check(checked)

    def check_row(self, checkbox_row, checked: bool):
        for checkbox, ypCell in checkbox_row.values():
            self.check_ypcell_box(checkbox, ypCell, checked)

    async def onSelectAllClick(self, msg: dict):
        """
        react on "select all" being clicked
        """
        try:
            checked = msg["checked"]
            for checkbox_row in self.checkboxes.values():
                self.check_row(checkbox_row, checked)
        except BaseException as ex:
            self.solution.handle_exception(ex)
        pass

    async def onSelectRowClick(self, msg: dict):
        """
        react on "select all " for a row being clicked
        """
        try:
            checked = msg["checked"]
            title = msg["target"].title
            context_name = title.replace("select all", "").strip()
            checkbox_row = self.checkboxes[context_name]
            self.check_row(checkbox_row, checked)
        except BaseException as ex:
            self.solution.handle_exception(ex)

    async def onSelectColumnClick(self, msg: dict):
        """
        react on "select all " for a column being clicked
        """
        try:
            checked = msg["checked"]
            title = msg["target"].title
            target_name = title.replace("select all", "").strip()
            for checkbox_row in self.checkboxes.values():
                checkbox, ypCell = checkbox_row[target_name]
                self.check_ypcell_box(checkbox, ypCell, checked)
        except BaseException as ex:
            self.solution.handle_exception(ex)

    async def onParentCheckboxClick(self, msg: dict):
        """
        a ypCell checkbox has been clicked for a ypCell that has subCells
        """
        # get the parent checkbox
        checkbox = msg.target
        checked = msg["checked"]
        # lookup the ypCell
        ypCell = self.ypcell_by_id[checkbox.id]
        self.checkSubCells(ypCell, checked)

    def displayTargets(self):
        # return self.targets.values()
        dt = []
        for target in self.targets.values():
            if target.showInGrid:
                dt.append(target)
        return dt

    def get_colums(self, target: Target) -> int:
        """
        get the number of columns for the given target
        
        Args:
            target(Target): the target
            
        Returns:
            int: the number of columns to be displayed
        """
        cols = 2 if target.is_multi else 1
        return cols

    def create_simple_checkbox(self, 
            parent, 
            label_text:str, 
            title:str, 
            classes:str=None, 
            on_change:Callable=None,
            **kwargs):
        """
        Create a NiceGUI checkbox with a label and optional tooltip, adding it to the specified parent container.
        
        Args:
            parent: The parent UI element to attach the checkbox to. Must be a NiceGUI container.
            label_text (str): The text label to display next to the checkbox.
            title (str): The tooltip text to display when hovering over the checkbox.
            classes (str, optional): CSS classes for additional styling. If None, uses a default.
            **kwargs: Additional keyword arguments to pass to the checkbox.
            
        Returns:
            ui.checkbox: The created checkbox instance.
        """
        if classes is None:
            classes = self.header_classes
        with parent:
            checkbox = ui.checkbox(
                label_text,
                **kwargs,
            )
            checkbox.classes(classes)
            checkbox.style(self.light_header_style)
            checkbox.tooltip(title)
        if on_change:
            checkbox.on("change",on_change)
        return checkbox

    def create_check_box(self, 
        yp_cell: YpCell, 
        parent,
        columns:int) -> ui.checkbox:
        """
        create a nicegui CheckBox for the given YpCell

        Args:
            yp_cell: YpCell - the YpCell to create a checkbox for
            parent: the nicegui parent element
            columns(int) the number of columns
  
        Returns:
            ui.checkbox: The created NiceGUI checkbox element.
        """
        with parent:
            label_text = yp_cell.getLabelText()
            checkbox = self.create_simple_checkbox(
                parent, 
                label_text,
                title=label_text
            ) 
            yp_cell.getPage(self.solution.smwAccess)
            color = "blue" if yp_cell.status == "✅" else "red"
            link = f"<a href='{yp_cell.pageUrl}' style='color:{color}'>{label_text}<a>"
            if yp_cell.status == "ⓘ":
                link = f"{label_text}"
            # in a one column setting we need to break link and status message
            if columns==1:
                label_text = label_text.replace(":", ":<br>")
                delim = "<br>"
            else:
                delim = "&nbsp;"
            link_html=ui.html()
            link_html.content=f"{link}{delim}"
            debug_div = ui.html()
            debug_div.content=f"{yp_cell.statusMsg}"
            hidden=getattr(self, "cell_hide_size_info", True)
            debug_div.visible=not hidden
            status_div = ui.html()
            status_div.content=yp_cell.status
            checkbox.status_div = status_div
            self.cell_debug_msg_divs.append(debug_div)
            # link ypCell with Checkbox via a unique identifier
            yp_cell.checkbox_id=checkbox.id
            self.ypcell_by_id[checkbox.id] = checkbox.id
            self.checkbox_by_id[checkbox.id] = checkbox
        return checkbox

    async def add_topic_rows(self, context: Context):
        """
        add the topic rows for the given context
        
        Args:
            context(Context): the context for which do add topic rows
        """
        def updateProgress():
            percent = progress_steps / total_steps * 100
            value = round(percent)
            self.solution.progressBar.update_value(value)
            self.grid.update()

        total_steps = 0
        for topic_name, topic in context.topics.items():
            total_steps += len(self.displayTargets())
            total_steps += len(topic.properties)
        progress_steps = 0
        updateProgress()
        for topic_name, topic in context.topics.items():
            self.checkboxes[topic_name] = {}
            checkbox_row = self.checkboxes[topic_name]
            with self.grid:                    
                icon_url = None
                if hasattr(topic, "iconUrl"):
                    if topic.iconUrl.startswith("http"):
                        icon_url = f"{topic.iconUrl}"
                if icon_url is not None and self.solution.mw_context is not None:
                    icon_url = f"{self.solution.mw_context.wiki_url}{topic.iconUrl}"
                if icon_url is None:
                    icon_url = "?"
                style=f'width: {self.iconSize}px; height: {self.iconSize}px;'
                _topic_icon = ui.image(
                    source=icon_url,
                ).style(style)
                checkbox=self.create_simple_checkbox(
                    parent=self.grid,
                    label_text="→",
                    title=f"select all {topic_name}",
                )
                checkbox.on('change',self.onSelectRowClick)
                for target in self.displayTargets():
                    progress_steps += 1
                    ypCell = YpCell.createYpCell(target=target, topic=topic)
                    if len(ypCell.subCells) > 0:
                        columns=self.get_colums(target)
                        prop_div_col = ui.grid(columns=columns)
                        with prop_div_col:     
                            prop_div = HideShow(
                                show_content=False,
                                hide_show_label=("properties", "properties"),
                            )
                            parent = prop_div
                    else:
                        parent = self.grid
                        columns=1
                    checkbox = self.create_check_box(ypCell, parent=parent, columns=columns)
                    checkbox_row[target.name] = (checkbox, ypCell)
                    if len(ypCell.subCells) > 0:
                        checkbox.on("input", self.onParentCheckboxClick)
                        for _prop_name, subCell in ypCell.subCells.items():
                            _subCheckBox = self.create_check_box(
                                subCell, parent=prop_div, columns=columns
                            )
                            progress_steps += 1
                            updateProgress()
                updateProgress()
            pass
        # done
        self.solution.progressBar.reset()

    def set_hide_show_status_of_cell_debug_msg(self, hidden: bool = False):
        """
        Sets the hidden status of all cell debug messages
        Args:
            hidden: If True hide debug messages else show them
        """
        self.cell_hide_size_info = hidden
        for div in self.cell_debug_msg_divs:
            div.visible=not hidden
