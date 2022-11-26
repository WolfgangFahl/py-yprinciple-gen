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
        pageTitle=f"{self.target.name}:{self.topic.name}"
        return pageTitle
        
    def getPageText(self,smwAccess:SMWAccess)->str:
        """
        get the pageText for the given smwAccess
        
        Args:
            smwAccess(SMWAccess): the Semantic Mediawiki access to use
            
        Returns:
            str: the wiki markup for this cell (if any)
        """
        pageTitle=self.getPageTitle()
        page=smwAccess.wikiClient.getPage(pageTitle)
        if page.exists:
            return page.text()
        else:
            return None
        
    def getStatus(self,smwAccess:SMWAccess):
        """
        get the pageText and status for the given smwAccess
        
        Args:
            smwAccess(SMWAccess): the Semantic Mediawiki access to use
            
        Returns:
            str: the wiki markup for this cell (if any)
        """
        if self.target.name=="Python":
            pageText=None
            status="ⓘ"
            status_msg=f"{status}"
        else:
            pageText=self.getPageText(smwAccess)
            status=f"✅" if pageText else "❌"
            status_msg=f"{len(pageText)}✅" if pageText else "❌"
        return pageText,status,status_msg


