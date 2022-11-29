'''
Created on 2022-11-25

@author: wf
'''
from meta.metamodel import MetaModelElement
from yprinciple.target import Target
from meta.mw import SMWAccess
from wikibot.wikipush import WikiPush
from yprinciple.editor import Editor
from yprinciple.version import Version

class YpCell:
    """
    a Y-Principle cell
    """
    
    def __init__(self,modelElement:MetaModelElement,target:Target,debug:bool=False):
        """
        constructor
        
        Args:
            modelElement(modelElement): the modelElement to generate for
            target(Target): the target to generate for
            debug(bool): if True - enable debugging 
        """
        self.modelElement=modelElement
        self.target=target
        self.smwAccess=None
        self.debug=debug
        self.subCells={}
        
    @classmethod
    def createYpCell(cls,target:Target,topic:'Topic',debug:bool=False)->'YpCell':
        """
        add a ypCell for the given target and topic
        """
        ypCell=YpCell(modelElement=topic,target=target,debug=debug)
        if target.is_multi:
            target.addSubCells(ypCell=ypCell,topic=topic,debug=debug)
        return ypCell
        
    def generate(self,smwAccess=None,dryRun:bool=True,withEditor:bool=False)->str:
        """
        generate the given cell and upload the result via the given
        Semantic MediaWiki Access
        
        Args:
            smwAccess(SMWAccess): the access to use
            dryRun(bool): if True do not push the result
            withEditor(bool): if True open Editor when in dry Run mode
            
        Returns:
            str: the markup diff
        """
        markup_diff=""
        # ignore multi targets
        if self.target.is_multi:
            return None
        markup=self.target.generate(self.modelElement)
        if withEditor:
            Editor.open_tmp_text(markup,file_name=self.target.getFileName(self.modelElement,"wiki_gen"))
        self.getPage(smwAccess)
        if self.pageText:
            markup_diff=WikiPush.getDiff(self.pageText, markup)
            if withEditor:
                Editor.open_tmp_text(self.pageText,file_name=self.target.getFileName(self.modelElement,"wiki_page"))
                Editor.open_tmp_text(markup_diff,file_name=self.target.getFileName(self.modelElement,"wiki_diff"))
        if not dryRun:
            self.page.edit(markup,f"modified by {Version.name} {Version.version}")
            # update status
            # @TODO make diff/status available
            self.getPage(smwAccess)
        return markup_diff
        
    def getLabelText(self)->str:
        """
        get my label Text
            
        Returns:
            str: a label in the generator grid for my modelElement 
        """
        return self.target.getLabelText(self.modelElement)
    
    def getPageTitle(self):
        """
        get the page title for my modelElement
        """
        return self.target.getPageTitle(self.modelElement)
    
    def getPage(self,smwAccess:SMWAccess)->str:
        """
        get the pageText and status for the given smwAccess
        
        Args:
            smwAccess(SMWAccess): the Semantic Mediawiki access to use
            
        Returns:
            str: the wiki markup for this cell (if any)
        """
        self.smwAccess=smwAccess
        self.pageUrl=None
        self.page=None
        self.pageText=None
        self.pageTitle=None
        if self.target.name=="Python" or self.target.is_multi:  
            self.status="ⓘ"
            self.statusMsg=f"{self.status}"
        else:
            wikiClient=smwAccess.wikiClient
            self.pageTitle=self.getPageTitle()
            self.page=wikiClient.getPage(self.pageTitle)
            baseurl=wikiClient.wikiUser.getWikiUrl()
            # assumes simple PageTitle without special chars
            # see https://www.mediawiki.org/wiki/Manual:Page_title for the more comples
            # rules that could apply
            self.pageUrl=f"{baseurl}/index.php/{self.pageTitle}"
            if self.page.exists:
                self.pageText=self.page.text()
            else:
                self.pageText=None
            self.status=f"✅" if self.pageText else "❌"
            self.statusMsg=f"{len(self.pageText)}✅" if self.pageText else "❌"     
        return self.page