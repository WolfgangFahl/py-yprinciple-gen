'''
Created on 2022-11-24

@author: wf
'''
import html
from nicegui import ui
from nicegui.client import Client
from meta.metamodel import Context
from meta.mw import SMWAccess
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.webserver import WebserverConfig
from wikibot3rd.wikiuser import WikiUser

from yprinciple.genapi import GeneratorAPI
from yprinciple.gengrid import GeneratorGrid
from yprinciple.smw_targets import SMWTarget
from yprinciple.version import Version
from ngwidgets.progress import NiceguiProgressbar

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
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = YPGenApp
        return server_config
    
    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(
            self, config=YPGenServer.get_config()
        )
        
    def configure_run(self):
        """
        """
        InputWebserver.configure_run(self)
        # wiki users
        self.wikiUsers=WikiUser.getWikiUsers()
    
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
        
    def prepare_ui(self):
        """
        prepare the user interface
        """
        super().prepare_ui()   
        args=self.args 
        # see https://wiki.bitplan.com/index.php/Y-Prinzip#Example
        self.targets=SMWTarget.getSMWTargets()
        self.wikiId=args.wikiId
        self.context_name=args.context
        
        self.wikiLink=None
        self.contextLink=None
  
        # states
        self.useSidif=True
        self.dryRun=True
        self.openEditor=False
        self.explainDepth=0
        # see also setGenApiFromWikiId    
        self.setGenApiFromArgs(args)
        
        
    def setGenApiFromArgs(self,args):
        """
        set the semantic MediaWiki
        """
        self.genapi=GeneratorAPI.fromArgs(args)
        self.genapi.setWikiAndGetContexts(args)
        self.smwAccess=self.genapi.smwAccess
        if self.wikiLink is not None:
            self.wikiLink.text=args.wikiId
            self.wikiLink.title=args.wikiId
            wikiUser=self.smwAccess.wikiClient.wikiUser
            if wikiUser:
                self.wikiLink.href=wikiUser.getWikiUrl()
        self.setMWContext()
        
    def setMWContext(self):
        """
        set my context
        """
        self.mw_contexts=self.genapi.mw_contexts
        mw_context=self.mw_contexts.get(self.context_name,None)
        if mw_context is not None:
            self.setContext(mw_context)
            
    def setContext(self,mw_context):
        """
        set the Context
        """
        self.mw_context=mw_context
        if self.contextLink is not None:
            if mw_context is not None:
                self.contextLink.title=f"{mw_context.context}({mw_context.since} at {mw_context.master}"
                self.contextLink.text=f"{mw_context.wikiId}:{mw_context.context}"
                self.contextLink.href=mw_context.sidif_url()
            else:
                self.contextLink.title="?"
                self.contextLink.text="?"
                self.contextLink.href="https://wiki.bitplan.com/index.php/Concept:Context"
    
   
    async def showGenerateGrid(self):
        """
        show the grid for generating code
        """
        # start with a new generatorGrid
        self.generatorGrid=GeneratorGrid(self.targets,parent=self.gridRows,solution=self)
        if self.useSidif:
            if self.mw_context is not None:
                context,error,errMsg=Context.fromWikiContext(self.mw_context, debug=self.args.debug,depth=self.explainDepth)
                if error is not None:
                    self.errors.inner_html=errMsg.replace("\n","<br>")
                else:
                    await self.generatorGrid.addRows(context)
            
    async def onPageReady(self,_msg):
        """
        react on page Ready
        """
        try:
            if len(self.gridRows.components)==0:
                await self.showGenerateGrid()
        except BaseException as ex:
            self.handleException(ex)
        
    async def onChangeLanguage(self,msg):
        """
        react on language being changed via Select control
        """
        self.language=msg.value  
        
    async def onChangeWikiUser(self,msg):
        """
        react on a the wikiuser being changed via a Select control
        """
        try:
            self.clearErrors()
            # change wikiUser
            self.args.wikiId=msg.value
            self.setGenApiFromArgs(self.args)
            await self.add_or_update_context_select()
            await self.wp.update()
        except BaseException as ex:
            self.handleException(ex)
        
    async def onChangeContext(self,msg):
        """
        react on the wikiuser being changed via a Select control
        """
        try:
            self.clearErrors()
            self.context_name=msg.value
            self.mw_context=self.mw_contexts.get(self.context_name,None)
            self.setContext(self.mw_context)
            await self.showGenerateGrid()
        except BaseException as ex:
            self.handleException(ex)
             
    def addLanguageSelect(self):
        """
        add a language selector
        """
        self.languageSelect=self.createSelect("Language","en",a=self.colB1,change=self.onChangeLanguage)
        for language in self.getLanguages():
            lang=language[0]
            desc=language[1]
            desc=html.unescape(desc)
            self.languageSelect.add(self.jp.Option(value=lang,text=desc))
            
    def addWikiUserSelect(self):
        """
        add a wiki user selector
        """
        if len(self.wikiUsers)>0:
            self.wikiuser_select=self.createSelect("wikiId", value=self.wikiId, change=self.onChangeWikiUser, a=self.colB1)
            for wikiUser in sorted(self.wikiUsers):
                self.wikiuser_select.add(self.jp.Option(value=wikiUser,text=wikiUser))
            if self.mw_context is not None:
                url=self.mw_context.wiki_url
                self.wikiLink=self.jp.A(a=self.colB2,title=self.wikiId,text=self.wikiId,href=url)
             
    def onExplainDepthChange(self,msg):
        self.explainDepth=int(msg.value)
                 
    def addExplainDepthSelect(self):
        self.explainDepthSelect=self.createSelect("explain depth",value=0,change=self.onExplainDepthChange,a=self.colB1)
        for depth in range(17):
            self.explainDepthSelect.add(self.jp.Option(value=depth,text=str(depth)))

    def handleHideShowSizeInfo(self, msg):
        """
        handles switching visibility of size information
        """
        show_size = msg.checked
        self.generatorGrid.set_hide_show_status_of_cell_debug_msg(hidden=not show_size)
                
    async def add_or_update_context_select(self):
        """
        add a selection of possible contexts for the given wiki
        """
        try:
            if self.contextSelect is None:
                self.contextSelect=self.createSelect("Context",value=self.context_name,change=self.onChangeContext,a=self.colC1)
                if self.mw_context is not None:
                    url=self.mw_context.sidif_url()
                else:
                    url="?"
                self.contextLink=self.jp.A(a=self.colC2,title=self.context_name,text=self.context_name,href=url)
            else:
                self.contextSelect.delete_components()
                self.setContext(None)
            for name,_mw_context in self.mw_contexts.items():
                self.contextSelect.add(self.jp.Option(value=name,text=name))
            await self.wp.update()
        except BaseException as ex:
            self.handleException(ex)
        
    def configure_settings(self):
        """
        override settings
        """
        self.addLanguageSelect()
        self.addWikiUserSelect()
        self.addExplainDepthSelect()
    
    async def home(self):
        """
        provide the main content / home page
  
        home page 
        """
        def show():
            """
            show the ui
            """
            self.progressBar = NiceguiProgressbar(total=100,desc="preparing",unit="steps")
            self.gridRows=ui.row()
            self.contextSelect=None
  
            #self.addWikiUserSelect()
            #await self.add_or_update_context_select()
            #self.wp.on("page_ready", self.onPageReady)
            
            self.useSidifButton=ui.switch("use SiDIF").bind_value(self,"useSidif")
            self.dryRunButton = ui.switch("dry Run").bind_value(self, 'dryRun')
            self.openEditorButton = ui.switch("open Editor").bind_value(self, 'openEditor')
            self.hideShowSizeInfo = ui.switch("size info").bind_value(self, 'hideShowSizeInfoState')
            
        await self.setup_content_div(show)