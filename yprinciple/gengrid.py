'''
Created on 25.11.2022

@author: wf
'''
from jpwidgets.bt5widgets import IconButton,SimpleCheckbox
from meta.metamodel import Context
from yprinciple.target import Target

class GeneratorGrid:
    """
    generator and selection grid
    
    see https://wiki.bitplan.com/index.php/Y-Prinzip#Example
    """
    
    def __init__(self,targets:list[Target],a,app):
        """
        constructor
        
        Args:
            targets(list[Target]): a list of targets
            a: the parent element
            app: the parent spp
            
        """
        self.gridRows=a
        self.app=app
        self.jp=app.jp
        self.wp=app.wp
        self.checkboxes={}
        self.targets=targets
        self.a=a
        self.gridHeaderRow=self.jp.Div(classes="row",name="gridHeaderRow",a=self.gridRows)
        self.headerClasses="col-1"
        self.downloadButton = IconButton(iconName="play",
                                                classes="btn btn-primary btn-sm col-1",
                                                a=self.gridHeaderRow,
                                                click=self.onGenerateButtonClick,
                                                disabled=False)
        self.targetsColumnHeader=self.jp.Div(text="Targets",a=self.gridHeaderRow,classes=self.headerClasses)
        self.targetSelectionHeader=self.jp.Div(a=self.gridRows,classes="row")
        self.jp.Label(a=self.targetSelectionHeader,classes="col-1")
        SimpleCheckbox(a=self.targetSelectionHeader, labelText="↘",title="select all",input=self.onSelectAllClick)
        for target in self.targets:
            self.jp.Div(a=self.gridHeaderRow,text=target.name,classes=self.headerClasses)
            SimpleCheckbox(labelText="↓", title=f"select all {target.name}",a=self.targetSelectionHeader,groupClasses=self.headerClasses,input=self.onSelectColumnClick)
   
    
    async def onGenerateButtonClick(self,msg):
        """
        react on the generate button having been clicked
        """
        
    async def onSelectAllClick(self,msg:dict):
        """
        react on "select all" being clicked
        """
        try:
            checked=msg["checked"]
            for checkbox_row in self.checkboxes.values():
                for checkbox in checkbox_row.values():
                    checkbox.check(checked)
        except BaseException as ex:
            self.app.handleException(ex)
        pass
        
    async def onSelectRowClick(self,msg:dict):
        """
        react on "select all " for a row being clicked
        """
        try:
            checked=msg["checked"]
            title=msg["target"].title
            context_name=title.replace("select all","").strip()
            checkbox_row=self.checkboxes[context_name]
            for checkbox in checkbox_row.values():
                checkbox.check(checked)
        except BaseException as ex:
            self.app.handleException(ex)
            
    async def onSelectColumnClick(self,msg:dict):
        """
        react on "select all " for a column being clicked
        """
        try:
            checked=msg["checked"]
            title=msg["target"].title
            target_name=title.replace("select all","").strip()
            for checkbox_row in self.checkboxes.values():
                checkbox=checkbox_row[target_name]
                checkbox.check(checked)
        except BaseException as ex:
            self.app.handleException(ex)
            
    
   
    def addRows(self,context:Context):
        """
        add the rows for the given topic
        """
        for topic_name,topic in context.topics.items():
            self.checkboxes[topic_name]={}
            checkbox_row=self.checkboxes[topic_name]
            _topicRow=self.jp.Div(a=self.gridRows,classes="row",style='color:black')
            _topicHeader=self.jp.Div(a=_topicRow,classes=self.headerClasses,text=topic_name)
            SimpleCheckbox(labelText="→",title=f"select all {topic_name}",a=_topicRow,groupClasses=self.headerClasses,input=self.onSelectRowClick)
            for target in self.targets:
                ylabel=target.labelFor(topic)
                checkbox_row[target.name]=SimpleCheckbox(labelText=ylabel, a=_topicRow, groupClasses="col-1")
            pass