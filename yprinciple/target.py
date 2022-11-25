'''
Created on 2022-11-25

@author: wf
'''

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