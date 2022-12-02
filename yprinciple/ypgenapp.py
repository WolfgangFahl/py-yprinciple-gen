'''
Created on 2022-11-24

@author: wf
'''
import os
import html
from jpcore.compat import Compatibility;Compatibility(0,11,3)
from jpcore.justpy_config import JpConfig
script_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = script_dir+"/resources/static"
JpConfig.set("STATIC_DIRECTORY",static_dir)
# shut up justpy
JpConfig.set("VERBOSE","False")
JpConfig.setup()
from jpwidgets.bt5widgets import App,About,ProgressBar,Switch,State
from wikibot.wikiuser import WikiUser
from meta.mw import SMWAccess
from meta.metamodel import Context
from yprinciple.smw_targets import SMWTarget
from yprinciple.gengrid import GeneratorGrid

class YPGenApp(App):
    """
    Y-Principle Generator Web Application
    """
    
    def __init__(self,version,title:str,args:None):
        '''
        Constructor
        
        Args:
            version(Version): the version info for the app
        '''
        import justpy as jp
        self.jp=jp
        App.__init__(self, version=version,title=title)
        self.args=args
        self.wikiId=args.wikiId
        self.context_name=args.context
        self.addMenuLink(text='Home',icon='home', href="/")
        self.addMenuLink(text='github',icon='github', href=version.cm_url)
        self.addMenuLink(text='Chat',icon='chat',href=version.chat_url)
        self.addMenuLink(text='Documentation',icon='file-document',href=version.doc_url)
        self.addMenuLink(text='Settings',icon='cog',href="/settings")
        self.addMenuLink(text='About',icon='information',href="/about")
        
        jp.Route('/settings',self.settings)
        jp.Route('/about',self.about)
        # wiki users
        self.wikiUsers=WikiUser.getWikiUsers()
        self.wikiLink=None
        self.contextLink=None
        self.setSMW(args.wikiId)
        # see https://wiki.bitplan.com/index.php/Y-Prinzip#Example
        self.targets=SMWTarget.getSMWTargets()
        # states
        self.useSidif=State(True)
        self.dryRun=State(True)
        self.openEditor=State(False)
        self.explainDepth=0
        
    def setSMW(self,wikiId:str):
        """
        set the semantic MediaWiki
        """
        self.smwAccess=SMWAccess(wikiId)
        self.mw_contexts=self.smwAccess.getMwContexts()
        self.mw_context=self.mw_contexts.get(self.context_name,None)
        self.setContext(self.mw_context)
        if self.wikiLink is not None:
            self.wikiLink.text=wikiId
            self.wikiLink.title=wikiId
            wikiUser=self.smwAccess.wikiClient.wikiUser
            if wikiUser:
                self.wikiLink.href=wikiUser.getWikiUrl()
            
    def setContext(self,mw_context):
        """
        set the Context
        """
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
        self.gridRows.delete_components()
        await self.wp.update()
        # start with a new generatorGrid
        self.generatorGrid=GeneratorGrid(self.targets,a=self.gridRows,app=self)
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
            self.setSMW(msg.value)
            await self.add_or_update_context_select()
            await self.wp.update()
        except BaseException as ex:
            self.handleException(ex)
        
    async def onChangeContext(self,msg):
        """
        react on a the wikiuser being changed via a Select control
        """
        try:
            self.clearErrors()
            self.context_name=msg.value
            self.mw_context=self.mw_contexts.get(self.context_name,None)
            self.setContext(self.mw_context)
            await self.showGenerateGrid()
        except BaseException as ex:
            self.handleException(ex)
        
    def setupRowsAndCols(self):
        """
        setup the general layout
        """
        head_html="""<link rel="stylesheet" href="/static/css/md_style_indigo.css">"""
        self.wp=self.getWp(head_html)
        self.button_classes = """btn btn-primary"""
        # rows
        self.rowA=self.jp.Div(classes="row",a=self.contentbox)
        self.rowB=self.jp.Div(classes="row",a=self.contentbox)
        self.rowC=self.jp.Div(classes="row",a=self.contentbox)
        self.rowD=self.jp.Div(classes="row",a=self.contentbox)
        self.rowE=self.jp.Div(classes="row",a=self.contentbox)
        # columns
        self.colA1=self.jp.Div(classes="col-12",a=self.rowA)
        self.colB1=self.jp.Div(classes="col-3",a=self.rowB)
        self.colB2=self.jp.Div(classes="col-2",a=self.rowB)
        self.colC1=self.jp.Div(classes="col-3",a=self.rowC)
        self.colC2=self.jp.Div(classes="col-2",a=self.rowC)
        self.colD1=self.jp.Div(classes="col-12",a=self.rowD)
        self.colE1=self.jp.Div(classes="col-12",a=self.rowE)
        # standard elements
        self.errors=self.jp.Div(a=self.colA1,style='color:red')
        self.messages=self.jp.Div(a=self.colE1,style='color:black')  
        self.progressBar = ProgressBar(a=self.rowC)
        self.gridRows=self.jp.Div(a=self.contentbox,name="gridRows") 
        self.contextSelect=None
        
    def addSwitch(self,a,labelText:str,state:State):
        """
        add a switch
        
        Args:
            a: parent Component
            labelText(str): label text for the switch
            field_wrap(list): pass by reference work around to allow a boolean
            variable to be modifie
            
        Returns:
            the switch component
        """ 
        button=Switch(a=a,labelText=labelText,state=state)
        return button
        
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
            self.wikiLink=self.jp.A(a=self.colB2,title=self.wikiId,text=self.wikiId,href=self.mw_context.wiki_url)
             
    def onExplainDepthChange(self,msg):
        self.explainDepth=int(msg.value)
                 
    def addExplainDepthSelect(self):
        self.explainDepthSelect=self.createSelect("explain depth",value=0,change=self.onExplainDepthChange,a=self.colB1)
        for depth in range(17):
            self.explainDepthSelect.add(self.jp.Option(value=depth,text=str(depth)))
                
    async def add_or_update_context_select(self):
        """
        add a selection of possible contexts for the given wiki
        """
        try:
            if self.contextSelect is None:
                self.contextSelect=self.createSelect("Context",value=self.context_name,change=self.onChangeContext,a=self.colC1)
                self.contextLink=self.jp.A(a=self.colC2,title=self.context_name,text=self.context_name,href=self.mw_context.sidif_url())
            else:
                self.contextSelect.delete_components()
                self.setContext(None)
            for name,_mw_context in self.mw_contexts.items():
                self.contextSelect.add(self.jp.Option(value=name,text=name))
            await self.wp.update()
        except BaseException as ex:
            self.handleException(ex)
        
    async def settings(self)->"jp.WebPage":
        '''
        settings
        
        Returns:
            jp.WebPage: a justpy webpage renderer
        '''
        self.setupRowsAndCols()
        self.addLanguageSelect()
        self.addWikiUserSelect()
        self.addExplainDepthSelect()
        return self.wp
    
    async def about(self)->"jp.WebPage":
        '''
        show about dialog
        
        Returns:
            jp.WebPage: a justpy webpage renderer
        '''
        self.setupRowsAndCols()
        self.aboutDiv=About(a=self.colB1,version=self.version)
        # @TODO Refactor to pyJustpyWidgets
        return self.wp
        
    async def content(self)->"jp.WebPage":
        '''
        provide the main content page
        
        Returns:
            jp.WebPage: a justpy webpage renderer
        '''
        self.setupRowsAndCols()
        self.addWikiUserSelect()
        await self.add_or_update_context_select()
        self.wp.on("page_ready", self.onPageReady)
        self.useSidifButton=self.addSwitch(a=self.colD1,labelText="use SiDIF",state=self.useSidif)
        self.dryRunButton=self.addSwitch(a=self.colD1,labelText="dry Run",state=self.dryRun)
        self.openEditorButton=self.addSwitch(a=self.colD1,labelText="open Editor",state=self.openEditor)
        return self.wp
    
    def start(self,host,port,debug):
        """
        start the server
        """
        self.debug=debug
        import justpy as jp
        jp.justpy(self.content,host=host,port=port)