'''
Created on 2022-11-25

@author: wf
'''
from meta.metamodel import Topic
from yprinciple.target import Target

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
        
    def getPageText(self,smwAccess):
        """
        test the pageText for the given smwAccess
        """
        pageTitle=self.getPageTitle()
        page=smwAccess.wikiClient.getPage(pageTitle)
        if page.exists:
            return page.text()
        else:
            return None
        


