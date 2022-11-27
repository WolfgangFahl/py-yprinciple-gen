'''
Created on 25.11.2022

@author: wf
'''
from jpwidgets.bt5widgets import IconButton,SimpleCheckbox
from meta.metamodel import Context
from yprinciple.ypcell import YpCell

class GeneratorGrid:
    """
    generator and selection grid
    
    see https://wiki.bitplan.com/index.php/Y-Prinzip#Example
    """
    
    def __init__(self,targets:dict,a,app,iconSize:str="32px"):
        """
        constructor
        
        Args:
            targets(dict): a list of targets
            a: the parent element
            app: the parent spp
            
        """
        self.gridRows=a
        self.app=app
        self.jp=app.jp
        self.wp=app.wp
        self.iconSize=iconSize
        self.checkboxes={}
        self.targets=targets
        self.a=a
        self.gridHeaderRow=self.jp.Div(classes="row",name="gridHeaderRow",a=self.gridRows)
        self.headerClasses="col-1 text-center"
        # see https://www.materialpalette.com/indigo/indigo
        # secondary text
        self.headerBackground="#c5cae9"
        self.lightHeaderBackground="#f5f5f5"
        bs_secondary="#6c757d"
        self.headerStyle=f"font-size: 1.0rem;background-color: {self.headerBackground}"
        self.lightHeaderStyle=f"background-color: {self.lightHeaderBackground}"
        self.generateButton = IconButton(iconName="play",
                                                classes="btn btn-primary btn-sm col-1",
                                                a=self.gridHeaderRow,
                                                click=self.onGenerateButtonClick,
                                                disabled=False)
        self.targetsColumnHeader=self.jp.Div(text="Targets",a=self.gridHeaderRow,
            classes=self.headerClasses,style=self.headerStyle)
        self.targetSelectionHeader=self.jp.Div(a=self.gridRows,classes="row")
        self.jp.Label(a=self.targetSelectionHeader,inner_html="<strong>Topics</strong>",classes=self.headerClasses,style=self.headerStyle)
        self.createSimpleCheckbox(a=self.targetSelectionHeader, labelText="↘",title="select all",input=self.onSelectAllClick)
        for target in self.targets.values():
            target_div=self.jp.Div(a=self.gridHeaderRow,classes=self.headerClasses,style=self.headerStyle)
            target_title=self.jp.Span(a=target_div,inner_html=target.name+"<br>",classes="align-middle")
            self.icon=self.jp.I(a=target_div,classes=f'mdi mdi-{target.icon_name}',style=f"color:{bs_secondary};font-size:{self.iconSize};")     
            self.createSimpleCheckbox(labelText="↓", title=f"select all {target.name}",a=self.targetSelectionHeader,input=self.onSelectColumnClick)
   
    def createSimpleCheckbox(self,labelText,title,a,**kwargs):
        """
        create a simple CheckBox with header style
        """
        classes=self.headerClasses
        style=self.lightHeaderStyle
        simpleCheckbox=SimpleCheckbox(labelText=labelText,title=title,a=a,classes=classes,style=style,**kwargs)
        return simpleCheckbox
    
    async def onGenerateButtonClick(self,_msg):
        """
        react on the generate button having been clicked
        """
        for checkbox_row in self.checkboxes.values():
            for checkbox,ypCell in checkbox_row.values():
                if checkbox.isChecked():
                    try:
                        ypCell.generate(smwAccess=self.app.smwAccess,dryRun=self.app.dryRun.value,withEditor=self.app.openEditor.value)
                        await self.app.wp.update()
                    except BaseException as ex:
                        self.app.handleException(ex)
        
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
            for checkbox,_ypcell in checkbox_row.values():
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
                checkbox,ypCell=checkbox_row[target_name]
                checkbox.check(checked)
        except BaseException as ex:
            self.app.handleException(ex)
            
   
    async def addRows(self,context:Context):
        """
        add the rows for the given topic
        """
        for topic_name,topic in context.topics.items():
            self.checkboxes[topic_name]={}
            checkbox_row=self.checkboxes[topic_name]
            _topicRow=self.jp.Div(a=self.gridRows,classes="row",style='color:black')
            topicHeader=self.jp.Div(a=_topicRow,text=topic_name,classes=self.headerClasses,style=self.headerStyle)
            icon_url=f"{topic.iconUrl}" if topic.iconUrl.startswith("http") else f"{self.app.mw_context.wiki_url}{topic.iconUrl}"
            _topicIcon=self.jp.Img(src=icon_url, a=topicHeader,width=f'{self.iconSize}',height=f'{self.iconSize}')
            self.createSimpleCheckbox(labelText="→",title=f"select all {topic_name}",a=_topicRow,input=self.onSelectRowClick)
            for target in self.targets.values():
                ypCell=YpCell(topic=topic,target=target)
                labelText=ypCell.getLabelText()
                labelText=labelText.replace(":",":<br>")
                checkbox=SimpleCheckbox(labelText="", a=_topicRow, groupClasses="col-1")
                ypCell.getPage(self.app.smwAccess)
                color="blue" if ypCell.status=="✅" else "red"
                link=f"<a href='{ypCell.pageUrl}' style='color:{color}'>{labelText}<a>"
                if ypCell.status=="ⓘ":
                    link=f"{labelText}"
                checkbox.label.inner_html=f"{link}<br>{ypCell.statusMsg}"
                checkbox_row[target.name]=(checkbox,ypCell)
                await self.app.wp.update()
            pass