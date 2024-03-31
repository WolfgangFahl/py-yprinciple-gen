"""
Created on 25.11.2022

@author: wf
"""
from typing import Callable, List
import uuid
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
        self.gridRows = parent
        self.solution = solution
        self.iconSize = iconSize
        self.checkboxes = {}
        self.ypcell_by_uuid = {}
        self.checkbox_by_uuid = {}
        self.targets = targets
        with self.gridRows:
            self.gridHeaderRow = ui.row()
        self.headerClasses = "col-1 text-center"
        # see https://www.materialpalette.com/indigo/indigo
        # secondary text
        self.headerBackground = "#c5cae9"
        self.lightHeaderBackground = "#f5f5f5"
        bs_secondary = "#6c757d"
        self.headerStyle = (
            f"font-size: 1.0rem;background-color: {self.headerBackground}"
        )
        self.lightHeaderStyle = f"background-color: {self.lightHeaderBackground}"
        with self.gridHeaderRow:
            self.generateButton = ui.button(
                iconName="play",
                classes="btn btn-primary btn-sm col-1",
                click=self.onGenerateButtonClick,
                disabled=False,
            )
            self.targetsColumnHeader = ui.row().classes(self.headerClasses).style(self.headerStyle),
        self.targetsColumnHeader.inner_html = "<strong>Target</strong>"
        with self.gridRows:
            self.targetSelectionHeader = ui.row()
            with self.targetSelectionHeader:
                ui.label("Topics").classes(self.headerClasses).style(self.headerStyle)
        self.create_simple_checkbox(
            parent=self.targetSelectionHeader,
            labelText="↘",
            title="select all",
            on_change=self.onSelectAllClick,
        )
        for target in self.displayTargets():
            columns=self.get_colums(target)
            with self.gridHeaderRow:
                target_div=ui.grid(columns=columns).classes("text-center").style(self.headerStyle)   
                with target_div:
                    target_title = ui.html().classes("align-middle")
                    target_title.content=target.name + "<br>"
                    self.icon = ui.icon(target.icon_name).style=f"color:{bs_secondary};font-size:{self.iconSize};",
            self.create_simple_checkbox(
                labelText="↓",
                title=f"select all {target.name}",
                parent=self.targetSelectionHeader,
                on_change=self.onSelectColumnClick,
            )
        self.cell_debug_msg_divs = []

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
                    checkbox = self.checkbox_by_uuid[subCell.checkbox_id]
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
            cell_checkbox = self.checkbox_by_uuid.get(ypCell.checkbox_id, None)
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
            checkbox = self.checkbox_by_uuid[subcell.checkbox_id]
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
        ypcell_uuid = checkbox.data["ypcell_uuid"]
        ypCell = self.ypcell_by_uuid[ypcell_uuid]
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
            on_change:Callable,
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
            classes = self.headerClasses
        with parent:
            checkbox = ui.checkbox(
                label=label_text,
                **kwargs,
            )
            checkbox.classes(classes)
            checkbox.style(self.lightHeaderStyle)
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
        label_text = yp_cell.getLabelText()
        checkbox = self.create_simple_checkbox(parent, label_text) 
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
        with checkbox:
            link_html=ui.html()
            link_html.content=f"{link}{delim}"
            content=ui.row().classes="flex flex-row gap-2"
            with content:
                debug_div = ui.html()
                debug_div.content=f"{yp_cell.statusMsg}"
                hidden=getattr(self, "cell_hide_size_info", True)
                debug_div.visible(not hidden)
                status_div = ui.html()
                status_div.content=yp_cell.status
                checkbox.status_div = status_div
                self.cell_debug_msg_divs.append(debug_div)
            # link ypCell with Checkbox via a unique identifier
            yp_cell.checkbox_id = uuid.uuid4()
            checkbox.data["ypcell_uuid"] = yp_cell.checkbox_id
            self.ypcell_by_uuid[yp_cell.checkbox_id] = yp_cell
            self.checkbox_by_uuid[yp_cell.checkbox_id] = checkbox
        return checkbox

    async def addRows(self, context: Context):
        """
        add the rows for the given topic
        """

        def updateProgress():
            percent = progress_steps / total_steps * 100
            value = round(percent)
            self.solution.progressBar.updateProgress(value)

        total_steps = 0
        for topic_name, topic in context.topics.items():
            total_steps += len(self.displayTargets())
            total_steps += len(topic.properties)
        progress_steps = 0
        updateProgress()
        for topic_name, topic in context.topics.items():
            self.checkboxes[topic_name] = {}
            checkbox_row = self.checkboxes[topic_name]
            with self.gridRows:
                topic_row=ui.row()
                with topic_row:
                    topic_header=ui.row().classes(self.headerClasses).style(self.headerStyle)
                    
            icon_url = None
            if hasattr(topic, "iconUrl"):
                if topic.iconUrl.startswith("http"):
                    icon_url = f"{topic.iconUrl}"
            if icon_url is not None and self.solution.mw_context is not None:
                icon_url = f"{self.solution.mw_context.wiki_url}{topic.iconUrl}"
            if icon_url is None:
                icon_url = "?"

            with topic_header:
                topic_icon = ui.image(
                    source=icon_url,
                    style=f'width: {self.iconSize}px; height: {self.iconSize}px;'
                )
            checkbox=self.create_simple_checkbox(
                parent=topic_row,
                labelText="→",
                title=f"select all {topic_name}",
            )
            checkbox.on('change',self.onSelectRowClick)
            for target in self.displayTargets():
                progress_steps += 1
                ypCell = YpCell.createYpCell(target=target, topic=topic)
                if len(ypCell.subCells) > 0:
                    with topic_row:
                        columns=self.get_colums(target)
                        prop_div_col = ui.grid(columns=columns)
                        with prop_div_col:     
                            prop_div = HideShow(
                                show_content=False,
                                hide_show_label=("properties", "properties"),
                            )
                            parent = prop_div
                else:
                    parent = topic_row
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
            div.visible(not hidden)
