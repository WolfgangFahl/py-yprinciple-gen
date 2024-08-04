"""
Created on 25.11.2022

@author: wf
"""

from typing import Callable, List

from meta.metamodel import Context, Topic
from ngwidgets.webserver import WebSolution
from ngwidgets.widgets import Link
from nicegui import run, ui
from nicegui.elements.tooltip import Tooltip

from yprinciple.target import Target
from yprinciple.ypcell import YpCell


class GeneratorGrid:
    """
    generator and selection grid

    see https://wiki.bitplan.com/index.php/Y-Prinzip#Example
    """

    def __init__(
        self, targets: dict, parent, solution: WebSolution, iconSize: str = "32px"
    ):
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
        self.cell_hide_size_info = True
        self.checkboxes = {}
        self.ypcell_by_id = {}
        self.checkbox_by_id = {}
        self.header_checkbox_by_id = {}
        self.cell_debug_msg_divs = []
        self.targets = targets
        self.setup_styles()
        self.setup_ui()

    def setup_ui(self):
        """
        setup the user interface
        """
        with self.parent:
            target_columns = len(self.displayTargets())
            # two more for the Topics and check box columns
            target_columns += 2
            self.grid = ui.grid(columns=target_columns).classes("w-full gap-0")
            self.setup_target_header_row()
            self.setup_topic_header_row()

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

    def add_header_cell(self, title: str):
        """
        add a header cell with the given title

        Args:
            title(str): the title of the cell
        """
        with self.grid:
            classes = self.header_classes + self.center_classes
            header_cell = ui.row().classes(classes).style(self.header_style)
            with header_cell:
                header_div = (
                    ui.html().classes(self.header_classes).style(self.header_style)
                )
                header_div.content = f"<strong>{title}</strong>"
        return header_cell

    def setup_target_header_row(self):
        """
        setup the header row
        """
        with self.grid:
            self.generateButton = ui.button(
                icon="play_circle", on_click=self.onGenerateButtonClick
            )
        self.targets_column_header = self.add_header_cell("Target")
        for target in self.displayTargets():
            target_header_cell = self.add_header_cell(target.name)
            with target_header_cell:
                ui.icon(target.icon_name, size=self.iconSize, color=self.bs_secondary)
                # <i class="mdi mdi-archive" style="color: rgb(108, 117, 125); font-size: 32px;"></i>
                # markup+=f"""<i class="mdi mdi-{target.icon_name}" style="color: {self.bs_secondary};font-size:{self.iconSize};"></i>"""
                # <i class="q-icon notranslate material-icons" aria-hidden="true" role="presentation" id="c48">archive</i>
                # markup+=f"""<i class="q-icon notranslate material-icons" aria-hidden="true" role="presentation">{target.icon_name}</i>"""
                pass

    def setup_topic_header_row(self):
        """
        setup the second header row
        """
        with self.grid:
            self.topics_column_header = (
                ui.html().classes(self.header_classes).style(self.header_style)
            )
            self.topics_column_header.content = "<strong>Topics</strong>"
        self.header_checkboxes = {}
        self.header_checkboxes["all"] = self.create_simple_checkbox(
            parent=self.grid,
            label_text="↘",
            title="select all",
            classes=self.center_classes,
            on_change=self.on_select_all,
        )
        for target in self.displayTargets():
            self.header_checkboxes[target.name] = self.create_simple_checkbox(
                parent=self.grid,
                label_text="↓",
                title=f"select all {target.name}",
                classes=self.center_classes,
                on_change=self.on_select_column,
            )

    def getCheckedYpCells(self) -> List[YpCell]:
        """
        get all checked YpCells
        """
        checkedYpCells = []
        # generate in order of rows
        for checkbox_row in self.checkboxes.values():
            for checkbox, ypCell in checkbox_row.values():
                if checkbox.value and ypCell.ui_ready:
                    checkedYpCells.append(ypCell)
                for subCell in ypCell.subCells.values():
                    if subCell.ui_ready:
                        checkbox = self.checkbox_by_id[subCell.checkbox_id]
                        if checkbox.value:
                            checkedYpCells.append(subCell)
        return checkedYpCells

    def generateCheckedCells(self, cellsToGen: List[YpCell]):
        try:
            # force login
            if not self.solution.smwAccess.wikiClient._is_logged_in:
                ex=self.solution.smwAccess.wikiClient.try_login()
                if ex:
                    self.solution.handle_exception(ex)
                    return
            for ypCell in cellsToGen:
                cell_checkbox = self.checkbox_by_id.get(ypCell.checkbox_id, None)
                status_div = cell_checkbox.status_div
                with status_div:
                    status_div.clear()
                    status_div.content = ""
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
                            link = Link.create(url=diff_url, text="Δ")
                            _link_html = ui.html(link).classes(
                                "text-xl font-bold " + delta_color,
                            )
                except BaseException as ex:
                    with status_div:
                        status_div.content = f"❗ error:{str(ex)}"
                    self.solution.handle_exception(ex)
                self.updateProgress()
        except Exception as outer_ex:
            self.solution.handle_exception(outer_ex)

    async def onGenerateButtonClick(self, _msg):
        """
        react on the generate button having been clicked
        """
        cellsToGen = self.getCheckedYpCells()
        total = len(cellsToGen)
        ui.notify(f"running {total} generator tasks")
        self.resetProgress("generating", total)
        await run.io_bound(self.generateCheckedCells, cellsToGen)

    def check_ypcell_box(self, checkbox, ypCell, checked: bool):
        """
        check the given checkbox and the ypCell belonging to it
        """
        checkbox.value = checked
        self.checkSubCells(ypCell, checked)

    def checkSubCells(self, ypCell, checked):
        # loop over all subcells
        for subcell in ypCell.subCells.values():
            # and set the checkbox value accordingly
            checkbox = self.checkbox_by_id[subcell.checkbox_id]
            checkbox.value = checked

    def check_row(self, checkbox_row, checked: bool):
        for checkbox, ypCell in checkbox_row.values():
            self.check_ypcell_box(checkbox, ypCell, checked)

    async def on_select_all(self, args):
        """
        react on "select all" being clicked
        """
        try:
            checked = args.value
            for checkbox_row in self.checkboxes.values():
                self.check_row(checkbox_row, checked)
        except BaseException as ex:
            self.solution.handle_exception(ex)
        pass

    def get_select(self, args) -> str:
        """
        get the select from the sender's tooltip
        """
        select = None
        slots = args.sender.slots.get("default")
        if slots:
            children = slots.children
            if len(children) > 0:
                tooltip = children[0]
                if isinstance(tooltip, Tooltip):
                    title = tooltip.text
                    select = title.replace("select all", "").strip()
        return select

    async def on_select_column(self, args):
        """
        react on "select all " for a column being clicked
        """
        try:
            checked = args.value
            target_name = self.get_select(args)
            if target_name:
                for checkboxes in self.checkboxes.values():
                    checkbox, ypCell = checkboxes[target_name]
                    self.check_ypcell_box(checkbox, ypCell, checked)
        except BaseException as ex:
            self.solution.handle_exception(ex)

    async def on_select_row(self, args):
        """
        react on "select all " for a row being clicked
        """
        try:
            checked = args.value
            topic_name = self.get_select(args)
            if topic_name:
                checkbox_row = self.checkboxes[topic_name]
                self.check_row(checkbox_row, checked)
        except BaseException as ex:
            self.solution.handle_exception(ex)

    async def onParentCheckboxClick(self, args):
        """
        a ypCell checkbox has been clicked for a ypCell that has subCells
        """
        # get the parent checkbox
        checkbox = args.sender
        checked = args.value
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

    def create_simple_checkbox(
        self,
        parent,
        label_text: str,
        title: str,
        classes: str = None,
        on_change: Callable = None,
        **kwargs,
    ):
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
                text=label_text,
                on_change=on_change,
                **kwargs,
            )
            checkbox.classes(classes)
            checkbox.style(self.light_header_style)
            checkbox.tooltip(title)
        return checkbox

    def create_check_box_for_cell(
        self, yp_cell: YpCell, parent, columns: int = 1
    ) -> ui.checkbox:
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
            yp_cell_card = ui.card()
        label_text = yp_cell.getLabelText()
        checkbox = self.create_simple_checkbox(
            parent=yp_cell_card, label_text=label_text, title=label_text
        )
        yp_cell.getPage(self.solution.smwAccess)
        color = "blue" if yp_cell.status == "✅" else "red"
        link = f"<a href='{yp_cell.pageUrl}' style='color:{color}'>{label_text}<a>"
        if yp_cell.status == "ⓘ":
            link = f"{label_text}"
        # in a one column setting we need to break link and status message
        if columns == 1:
            label_text = label_text.replace(":", ":<br>")
            delim = "<br>"
        else:
            delim = "&nbsp;"
        with yp_cell_card:
            link_html = ui.html()
            link_html.content = f"{link}{delim}"
            debug_div = ui.html()
            debug_div.content = f"{yp_cell.statusMsg}"
            debug_div.visible = not self.cell_hide_size_info
            status_div = ui.html()
            status_div.content = yp_cell.status
            checkbox.status_div = status_div
            self.cell_debug_msg_divs.append(debug_div)
        # link ypCell with check box via a unique identifier
        yp_cell.checkbox_id = checkbox.id
        self.ypcell_by_id[checkbox.id] = checkbox.id
        self.checkbox_by_id[checkbox.id] = checkbox
        yp_cell.ui_ready = True
        return checkbox

    def add_topic_cell(self, topic: Topic):
        """
        add an icon for the given topic
        """
        topic_cell = self.add_header_cell(topic.name)
        icon_url = None
        if hasattr(topic, "iconUrl"):
            if topic.iconUrl.startswith("http"):
                icon_url = f"{topic.iconUrl}"
            if icon_url is None and self.solution.mw_context is not None:
                icon_url = f"{self.solution.mw_context.wiki_url}{topic.iconUrl}"
        if icon_url is None:
            icon_url = "?"
        style = f"width: {self.iconSize}; height: {self.iconSize};"
        with topic_cell:
            topic_icon = ui.image(
                source=icon_url,
            )
        topic_icon.style(style)
        return topic_icon

    def resetProgress(self, desc: str, total: int):
        self.solution.progressBar.desc = desc
        self.solution.progressBar.total = total
        self.solution.progressBar.reset()

    def updateProgress(self):
        """
        update the progress
        """
        self.solution.progressBar.update(1)
        self.grid.update()

    def add_yp_cell(self, parent, ypCell: YpCell) -> "ui.checkbox":
        """
        add the given ypCell
        """
        if len(ypCell.subCells) > 0:
            checkbox = None
            with parent:
                # content_div=ui.row()
                hide_show = ui.expansion("", icon="format_list_bulleted").classes(
                    "w-full"
                )
                # hide_show = HideShow(
                #    show_content=False,
                #    hide_show_label=("properties", "properties"),
                #    content_div=content_div
                # )
            for _subcell_name, subCell in ypCell.subCells.items():
                checkbox = self.create_check_box_for_cell(subCell, parent=hide_show)
                self.updateProgress()
                pass
        else:
            checkbox = self.create_check_box_for_cell(ypCell, parent=self.grid)
            self.updateProgress()
        return checkbox

    def add_topic_rows(self, context: Context):
        """
        add the topic rows for the given context

        Args:
            context(Context): the context for which do add topic rows
        """
        total_steps = 0
        for topic_name, topic in context.topics.items():
            total_steps += len(self.displayTargets()) - 1
            total_steps += len(topic.properties)
        self.resetProgress("preparing", total=total_steps)
        for topic_name, topic in context.topics.items():
            self.checkboxes[topic_name] = {}
            checkbox_row = self.checkboxes[topic_name]
            with self.grid:
                self.add_topic_cell(topic)
                checkbox = self.create_simple_checkbox(
                    parent=self.grid,
                    label_text="→",
                    title=f"select all {topic_name}",
                    on_change=self.on_select_row,
                )
            for target in self.displayTargets():
                ypCell = YpCell.createYpCell(target=target, topic=topic)
                checkbox = self.add_yp_cell(parent=self.grid, ypCell=ypCell)
                if checkbox:
                    checkbox_row[target.name] = (checkbox, ypCell)
            pass

    def set_hide_show_status_of_cell_debug_msg(self, hidden: bool = False):
        """
        Sets the hidden status of all cell debug messages
        Args:
            hidden: If True hide debug messages else show them
        """
        try:
            self.cell_hide_size_info = hidden
            for div in self.cell_debug_msg_divs:
                div.visible = not hidden
            self.grid.update()
        except Exception as ex:
            self.solution.handle_exception(ex)
