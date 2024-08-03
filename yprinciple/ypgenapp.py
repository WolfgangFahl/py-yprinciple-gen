"""
Created on 2022-11-24

@author: wf
"""

import html

from meta.metamodel import Context
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.profiler import Profiler
from ngwidgets.progress import NiceguiProgressbar
from ngwidgets.webserver import WebserverConfig
from ngwidgets.widgets import Link
from nicegui import background_tasks, run, ui
from nicegui.client import Client
from wikibot3rd.wikiuser import WikiUser

from yprinciple.genapi import GeneratorAPI
from yprinciple.gengrid import GeneratorGrid
from yprinciple.smw_targets import SMWTarget
from yprinciple.version import Version


class YPGenServer(InputWebserver):
    """
    Y-Principle Generator webserver
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        """
        get the configuration for this Webserver
        """
        copy_right = ""
        config = WebserverConfig(
            short_name="ypgen",
            copy_right=copy_right,
            version=Version(),
            default_port=8778,
            timeout=7.5,
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = YPGenApp
        return server_config

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(self, config=YPGenServer.get_config())

    def configure_run(self):
        """ """
        InputWebserver.configure_run(self)
        # wiki users
        self.wikiUsers = WikiUser.getWikiUsers()


class YPGenApp(InputWebSolution):
    """
    Y-Principle Generator Web Application / Solution
    """

    def __init__(self, webserver: YPGenServer, client: Client):
        """
        Initializes the InputWebSolution instance with the webserver and client.

        Args:
            webserver (NiceGuiWebserver): The webserver instance this solution is part of.
            client (Client): The client interacting with this solution.
        """
        super().__init__(webserver, client)

    def clearErrors(self):
        """
        clear log entries
        """
        self.log_view.clear()

    def prepare_ui(self):
        """
        prepare the user interface
        """
        super().prepare_ui()
        args = self.args
        profile = Profiler("prepare_ui", profile=args.debug)
        self.wikiUsers = self.webserver.wikiUsers
        # see https://wiki.bitplan.com/index.php/Y-Prinzip#Example
        smw_profile = Profiler("get SMW targets", profile=args.debug)
        self.targets = SMWTarget.getSMWTargets()
        smw_profile.time()
        self.wikiId = args.wikiId
        self.context_name = args.context

        self.wikiLink = None
        self.mw_context = None
        self.mw_contexts = {}
        self.contextLink = None

        # states
        self.useSidif = True
        self.dryRun = True
        self.openEditor = False
        self.explainDepth = 0
        profile.time()

    def setWikiLink(self, url, text, tooltip):
        if self.wikiLink is not None:
            link = Link.create(url, text, tooltip)
            self.wikiLink.content = link

    def setGenApiFromArgs(self, args=None):
        """
        set the semantic MediaWiki
        """
        if args is None:
            args = self.args
        with self.content_div:
            ui.notify("preparing Generator")
        self.setGeneratorEnvironmentFromArgs(args)

    def setGeneratorEnvironmentFromArgs(self, args):
        """
        set my generator environment from the given command line arguments
        """
        gen_profile = Profiler("prepare gen API and mwcontext", profile=self.args.debug)
        self.genapi = GeneratorAPI.fromArgs(args)
        self.genapi.setWikiAndGetContexts(args)
        self.smwAccess = self.genapi.smwAccess
        wikiUser = self.smwAccess.wikiClient.wikiUser
        if wikiUser:
            self.setWikiLink(wikiUser.getWikiUrl(), args.wikiId, args.wikiId)
        self.setMWContext()
        gen_profile.time()

    def setMWContext(self):
        """
        set my context
        """
        self.mw_contexts = self.genapi.mw_contexts
        mw_context = self.mw_contexts.get(self.context_name, None)
        self.setContext(mw_context)

    def setContext(self, mw_context):
        """
        set the Context
        """
        self.mw_context = mw_context
        if self.contextLink is not None:
            if mw_context is not None:
                self.contextLink.title = (
                    f"{mw_context.context}({mw_context.since} at {mw_context.master}"
                )
                self.contextLink.text = f"{mw_context.wikiId}:{mw_context.context}"
                self.contextLink.href = mw_context.sidif_url()
            else:
                self.contextLink.title = "?"
                self.contextLink.text = "?"
                self.contextLink.href = (
                    "https://wiki.bitplan.com/index.php/Concept:Context"
                )

    async def async_showGenerateGrid(self):
        """
        run setup in background
        """
        await run.io_bound(self.show_GenerateGrid)

    def show_GenerateGrid(self):
        """
        show the grid for generating code
        """
        try:
            self.grid_container.clear()
            with self.grid_container:
                # start with a new generatorGrid
                self.generatorGrid = GeneratorGrid(
                    self.targets, parent=self.grid_container, solution=self
                )
            if self.useSidif:
                if self.mw_context is not None:
                    context, error, errMsg = Context.fromWikiContext(
                        self.mw_context, debug=self.args.debug, depth=self.explainDepth
                    )
                    if error is not None:
                        self.log_view.push(errMsg)
                    else:
                        self.generatorGrid.add_topic_rows(context)
        except Exception as ex:
            self.handle_exception(ex)

    async def onChangeLanguage(self, msg):
        """
        react on language being changed via Select control
        """
        self.language = msg.value

    async def onChangeWiki(self, e):
        """
        react on a the wiki being changed
        via a Select control
        """
        try:
            wikiId = e.value
            self.clearErrors()
            # change wikiUser
            self.args.wikiId = wikiId
            await run.io_bound(self.setGeneratorEnvironmentFromArgs, self.args)
            await self.update_context_select()
        except BaseException as ex:
            self.handle_exception(ex)

    async def onChangeContext(self, msg):
        """
        react on the context
        being changed via a Select control
        """
        try:
            self.clearErrors()
            self.context_name = msg.value
            self.mw_context = self.mw_contexts.get(self.context_name, None)
            self.setContext(self.mw_context)
            self.update_context_link()
            await self.async_showGenerateGrid()
        except BaseException as ex:
            self.handle_exception(ex)

    def addLanguageSelect(self):
        """
        add a language selector
        """
        self.languageSelect = self.createSelect(
            "Language", "en", a=self.colB1, change=self.onChangeLanguage
        )
        for language in self.getLanguages():
            lang = language[0]
            desc = language[1]
            desc = html.unescape(desc)
            self.languageSelect.add(self.jp.Option(value=lang, text=desc))

    def addWikiSelect(self):
        """
        add a wiki selector
        """
        if len(self.wikiUsers) > 0:
            self.wiki_select = self.add_select(
                title="wikiId",
                selection=sorted(self.wikiUsers),
                value=self.wikiId,
                on_change=self.onChangeWiki,
            )
            if self.mw_context is not None:
                self.wikiLink = ui.html()
                url = self.mw_context.wiki_url
                self.setWikiLink(url=url, text=self.wikiId, tooltip=self.wikiId)

    def onExplainDepthChange(self, msg):
        self.explainDepth = int(msg.value)

    def addExplainDepthSelect(self):
        self.explainDepthSelect = self.createSelect(
            "explain depth", value=0, change=self.onExplainDepthChange, a=self.colB1
        )
        for depth in range(17):
            self.explainDepthSelect.add(self.jp.Option(value=depth, text=str(depth)))

    def handleHideShowSizeInfo(self, msg):
        """
        handles switching visibility of size information
        """
        show_size = msg.sender.value
        self.generatorGrid.set_hide_show_status_of_cell_debug_msg(hidden=not show_size)

    def add_context_select(self):
        """
        add a selection of possible contexts for the given wiki
        """
        try:
            selection = list(self.mw_contexts.keys())
            self.context_select = self.add_select(
                "Context",
                selection=selection,
                value=self.context_name,
                on_change=self.onChangeContext,
            )
            self.context_link = ui.html()
            self.update_context_link()
        except BaseException as ex:
            self.handle_exception(ex)

    def update_context_link(self):
        """
        update the context link
        """
        if self.mw_context is not None:
            url = self.mw_context.sidif_url()
            link = Link.create(url, text=self.context_name)
            self.context_link.content = link
        else:
            self.context_link.content = "?"

        self.context_link.update()
        pass

    async def update_context_select(self):
        """
        react on update of context select
        """
        self.update_context_link()
        context_selection = list(self.mw_contexts.keys())
        self.context_select.options = context_selection
        if self.context_name in context_selection:
            self.context_select.value = self.context_name
        self.context_select.update()
        self.grid_container.clear()
        pass

    def configure_settings(self):
        """
        override settings
        """
        self.addLanguageSelect()
        self.addWikiSelect()
        self.addExplainDepthSelect()

    async def show_all(self):
        """
        show settings and generator grid
        """
        with self.content_div:
            self.content_div.clear()
            with ui.card() as self.settings_area:
                with ui.grid(columns=2):
                    self.addWikiSelect()
                    self.add_context_select()
            with ui.row() as self.button_bar:
                self.tool_button(
                    tooltip="reload",
                    icon="refresh",
                    handler=self.async_showGenerateGrid,
                )
                self.useSidifButton = ui.switch("use SiDIF").bind_value(
                    self, "useSidif"
                )
                self.dryRunButton = ui.switch("dry Run").bind_value(self, "dryRun")
                self.openEditorButton = ui.switch("open Editor").bind_value(
                    self, "openEditor"
                )
                self.hideShowSizeInfo = ui.switch("size info").on(
                    "click", self.handleHideShowSizeInfo
                )
            with ui.row() as self.progress_container:
                self.progressBar = NiceguiProgressbar(
                    total=100, desc="preparing", unit="steps"
                )
            with ui.row() as self.grid_container:
                pass

    async def load_home_page(self):
        """
        back ground preparation
        """
        with self.content_div:
            # show a spinner while loading
            ui.spinner()
        await run.io_bound(self.setGenApiFromArgs)
        self.content_div.clear()
        await self.show_all()

    async def home(self):
        """
        provide the main content / home page

        home page
        """

        def show():
            """
            show the ui
            """
            try:
                # run view
                background_tasks.create(self.load_home_page())
            except Exception as ex:
                self.handle_exception(ex)

        await self.setup_content_div(show)
