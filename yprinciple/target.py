'''
Created on 2022-11-25

@author: wf
'''

class Target:
    """
    a generator Target on the technical side of the Y-Principle
    """
    
    def __init__(self,name:str,icon_name:str="bullseye",is_multi:bool=False,is_subtarget=False,subTarget=None):
        """
        constructor
        name(str): the name of the target
        icon_name(str): the icon_name of the target
        is_multi(bool): if True this target creates a list of results (has subtargets)
        is_subtarget(bool): if True this target has subtargets
        subTarget(object): the subTarget (if any)
        
        """
        self.name=name
        self.icon_name=icon_name
        self.is_multi=is_multi
        self.is_subtarget=is_subtarget
        self.subTarget=subTarget
        
    def getLabelText(self,modelElement)->str:
        return self.getPageTitle(modelElement)
    
    def getPageTitle(self,modelElement)->str:
        pageTitle=f"{self.name}:{modelElement.name}"
        return pageTitle   
        
    def generate(self,topic:'Topic')->str:
        """
        generate a result for the given topic
        """
        raise Exception(f"No generator available for target {self.name}")
        