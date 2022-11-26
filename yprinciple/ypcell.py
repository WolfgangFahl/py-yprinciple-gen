'''
Created on 2022-11-25

@author: wf
'''
from meta.metamodel import Topic
from yprinciple.target import Target
from meta.mw import SMWAccess

class YpCell:
    """
    a Y-Principle cell
    """
    
    def __init__(self,topic:Topic,target:Target):
        """
        constructor
        
        Args:
            topic(Topic): the topic to generate for
            target(): the target to generate for
        """
        self.topic=topic
        self.target=target
        self.smwAccess=None
        
    def generate(self,smwAccess=None):
        """
        """
        self.target.generate(self.topic)
        
        
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
            if self.page.exists:
                baseurl=wikiClient.wikiUser.getWikiUrl()
                # assumes simple PageTitle without special chars
                # see https://www.mediawiki.org/wiki/Manual:Page_title for the more comples
                # rules that could apply
                self.pageUrl=f"{baseurl}/index.php/{self.pageTitle}"
                self.pageText=self.page.text()
            else:
                self.pageText=None
            self.status=f"✅" if self.pageText else "❌"
            self.statusMsg=f"{len(self.pageText)}✅" if self.pageText else "❌"     
        return self.page