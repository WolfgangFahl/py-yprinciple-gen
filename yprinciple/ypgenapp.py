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
from jpwidgets.bt5widgets import App,Link,About
from wikibot.wikiuser import WikiUser
from meta.mw import SMWAccess

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
        self.setSMW(args.wikiId)
        
    def setSMW(self,wikiId:str):
        self.smwAccess=SMWAccess(wikiId)
        self.mw_contexts=self.smwAccess.getMwContexts()
        self.mw_context=self.mw_contexts.get(self.context_name,None)
        
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
            self.setSMW(msg.value)
            self.add_or_update_context_select()
            await self.wp.update()
        except BaseException as ex:
            self.handleException(ex)
        
    async def onChangeContext(self,msg):
        """
        react on a the wikiuser being changed via a Select control
        """
        self.context_name=msg.value
        self.mw_context=self.mw_contexts.get(self.context_name,None)
        
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
        # columns
        self.colA1=self.jp.Div(classes="col-12",a=self.rowA)
        self.colB1=self.jp.Div(classes="col-6",a=self.rowB)
        self.colB2=self.jp.Div(classes="col-6",a=self.rowB)
        self.colC1=self.jp.Div(classes="col-12",a=self.rowC,style='color:black')
        # standard elements
        self.errors=self.jp.Div(a=self.colA1,style='color:red')
        self.messages=self.jp.Div(a=self.colC1,style='color:black')   
        self.contextSelect=None
        
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
                
    def add_or_update_context_select(self):
        """
        add a selection of possible contexts for the given wiki
        """
        try:
            if self.contextSelect is None:
                self.contextSelect=self.createSelect("Context",value=self.context_name,change=self.onChangeContext,a=self.colB1)
            else:
                self.contextSelect.components.clear()
            for name,_mw_context in self.mw_contexts.items():
                self.contextSelect.add(self.jp.Option(value=name,text=name))
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
        self.add_or_update_context_select()
        return self.wp
    
    def start(self,host,port,debug):
        """
        start the server
        """
        self.debug=debug
        import justpy as jp
        jp.justpy(self.content,host=host,port=port)