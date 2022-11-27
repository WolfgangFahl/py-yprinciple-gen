'''
Created on 2022-11-25

@author: wf
'''
from meta.metamodel import Topic
from yprinciple.target import Target
from meta.mw import SMWAccess
from wikibot.wikipush import WikiPush
from yprinciple.editor import Editor
from yprinciple.version import Version

class YpCell:
    """
    a Y-Principle cell
    """
    
    def __init__(self,topic:Topic,target:Target,debug:bool=False):
        """
        constructor
        
        Args:
            topic(Topic): the topic to generate for
            target(Target): the target to generate for
            debug(bool): if True - enable debugging 
        """
        self.topic=topic
        self.target=target
        self.smwAccess=None
        self.debug=debug
        
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
        target_key=self.target.target_key
        markup=self.target.generate(self.topic)
        if withEditor:
            Editor.open_tmp_text(markup,file_name=f"{target_key}_gen.wiki")
        self.getPage(smwAccess)
        if self.pageText:
            markup_diff=WikiPush.getDiff(self.pageText, markup)
            if withEditor:
                Editor.open_tmp_text(markup,file_name=f"{target_key}_gen.wiki")
                Editor.open_tmp_text(self.pageText,file_name=f"{target_key}_markup.wiki")
                Editor.open_tmp_text(markup_diff,file_name=f"{target_key}_diff.txt")
        if not dryRun:
            self.page.edit(markup,f"modified by {Version.name} {Version.version}")
            # update status
            # @TODO make diff/status available
            self.getPage(smwAccess)
        return markup_diff
        
    def getLabelText(self)->str:
        """
        get my label Text
        
        Args:
            topic(Topic): the topic
            
        Returns:
            str: a label in the generator grid for the topic
        """
        labelText=f"{self.target.name}:{self.topic.name}"
        return labelText
    
    def getPageTitle(self):
        """
        get the page title
        """
        if self.target.name=="List of":
            pageTitle=f"List of {self.topic.pluralName}"
        else:
            pageTitle=f"{self.target.name}:{self.topic.name}"
        return pageTitle
    
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