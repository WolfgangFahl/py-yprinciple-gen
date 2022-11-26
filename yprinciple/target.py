'''
Created on 2022-11-25

@author: wf
'''

class Target:
    """
    a generator Target on the technical side of the Y-Principle
    """
    
    def __init__(self,name:str,icon_name:str="bullseye",is_multi:bool=False):
        """
        constructor
        
        name(str): the name of the target
        icon_name(str): the icon_name of the target
        is_multi(bool): if True this target creates a list of results
        """
        self.name=name
        self.icon_name=icon_name
        self.is_multi=is_multi
        
    @classmethod
    def getSMWTargets(cls):
        targets=[
            Target("Category","archive"),
            Target("Concept","puzzle"),
            Target("Form","form-select"),
            Target("Help","help-box"),
            Target("List of","format-list-bulleted"),
            Target("Template","file-document"),
            Target("Properties","alpha-p-circle",is_multi=True),
            Target("Python","snake")]
        return targets