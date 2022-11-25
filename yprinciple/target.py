'''
Created on 2022-11-25

@author: wf
'''
from meta.metamodel import Topic
class Target:
    """
    a generator Target on the technical side of the Y-Principle
    """
    
    def __init__(self,name:str,icon_name:str="bullseye"):
        """
        constructor
        
        name(str): the name of the target
        icon_name(str): the icon_name of the target
        """
        self.name=name
        self.icon_name=icon_name
        
    def labelFor(self,topic:Topic)->str:
        """
        get the label for the given topic
        
        Args:
            topic(Topic): the topic
            
        Returns:
            str: a label in the generator grid for the topic
        """
        label=f"{self.name}:{topic.name}"
        return label
