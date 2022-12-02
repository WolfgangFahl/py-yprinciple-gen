'''
Created on 25.11.2022

@author: wf
'''
from jpwidgets.bt5widgets import IconButton,SimpleCheckbox
from jpwidgets.widgets import HideShow
from meta.metamodel import Context
from yprinciple.ypcell import YpCell
from yprinciple.target import Target
import uuid

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
        self.ypcell_by_uuid={}
        self.checkbox_by_uuid={}
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
        self.targetsColumnHeader.inner_html="<strong>Target</strong>"
        self.targetSelectionHeader=self.jp.Div(a=self.gridRows,classes="row")
        self.jp.Label(a=self.targetSelectionHeader,inner_html="<strong>Topics</strong>",classes=self.headerClasses,style=self.headerStyle)
        self.createSimpleCheckbox(a=self.targetSelectionHeader, labelText="↘",title="select all",input=self.onSelectAllClick)
        for target in self.displayTargets():
            classes=self.getCols(target)
            target_div=self.jp.Div(a=self.gridHeaderRow,classes=classes+" text-center",style=self.headerStyle)
            target_title=self.jp.Span(a=target_div,inner_html=target.name+"<br>",classes="align-middle")
            self.icon=self.jp.I(a=target_div,classes=f'mdi mdi-{target.icon_name}',style=f"color:{bs_secondary};font-size:{self.iconSize};")     
            self.createSimpleCheckbox(labelText="↓", title=f"select all {target.name}",a=self.targetSelectionHeader,classes=classes,input=self.onSelectColumnClick)
    
    def getCheckedYpCells(self):
        """
        get all checked YpCells
        """
        checkedYpCells=[]
        # generate in order of rows
        for checkbox_row in self.checkboxes.values():
            for checkbox,ypCell in checkbox_row.values():
                if checkbox.isChecked():
                    checkedYpCells.append(ypCell)
                for subCell in ypCell.subCells.values():
                    checkbox=self.checkbox_by_uuid[subCell.checkbox_id]
                    if checkbox.isChecked():
                        checkedYpCells.append(subCell)
        return checkedYpCells
                
        
    async def onGenerateButtonClick(self,_msg):
        """
        react on the generate button having been clicked
        """
        cellsToGen=self.getCheckedYpCells()
        for ypCell in cellsToGen:
            try:
                ypCell.generate(smwAccess=self.app.smwAccess,dryRun=self.app.dryRun.value,withEditor=self.app.openEditor.value)
                await self.app.wp.update()
            except BaseException as ex:
                self.app.handleException(ex)
                    
    def check_ypcell_box(self,checkbox,ypCell,checked:bool):
        """
        check the given checkbox and the ypCell belonging to it
        """
        checkbox.check(checked)
        self.checkSubCells(ypCell,checked)
        
    def checkSubCells(self,ypCell,checked):
        # loop over all subcells
        for subcell in ypCell.subCells.values():
            # and set the checkbox value accordingly
            checkbox=self.checkbox_by_uuid[subcell.checkbox_id]
            checkbox.check(checked)
                        
    def check_row(self,checkbox_row,checked:bool):
        for checkbox,ypCell in checkbox_row.values():
            self.check_ypcell_box(checkbox,ypCell,checked)
        
    async def onSelectAllClick(self,msg:dict):
        """
        react on "select all" being clicked
        """
        try:
            checked=msg["checked"]
            for checkbox_row in self.checkboxes.values():
                self.check_row(checkbox_row,checked)
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
            self.check_row(checkbox_row,checked)
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
                self.check_ypcell_box(checkbox,ypCell,checked)
        except BaseException as ex:
            self.app.handleException(ex)
            
    async def onParentCheckboxClick(self,msg:dict):
        """
        a ypCell checkbox has been clicked for a ypCell that has subCells
        """
        # get the parent checkbox
        checkbox=msg.target
        checked=msg["checked"]
        # lookup the ypCell
        ypcell_uuid=checkbox.data["ypcell_uuid"]
        ypCell=self.ypcell_by_uuid[ypcell_uuid]
        self.checkSubCells(ypCell, checked)
            
    def displayTargets(self):
        #return self.targets.values()
        dt=[]
        for target in self.targets.values():
            if target.showInGrid:
                dt.append(target)
        return dt
    
    def getCols(self,target:Target)->str:
        cols="col-2" if target.is_multi else "col-1"
        return cols
    
    def createSimpleCheckbox(self,labelText,title,a,classes=None,**kwargs):
        """
        create a simple CheckBox with header style
        """
        if classes is None:
            classes=self.headerClasses
        style=self.lightHeaderStyle
        simpleCheckbox=SimpleCheckbox(labelText=labelText,title=title,a=a,classes=classes,style=style,**kwargs)
        return simpleCheckbox
            
    def createCheckBox(self,ypCell:YpCell,a,classes="col-1")->SimpleCheckbox:
        """
        create a CheckBox for the given YpCell
        
        Args:
            ypCell: YpCell - the YpCell to create a checkbox for
            
        Returns:
            SimpleCheckbox: the checkbox for the given cell
        """
        labelText=ypCell.getLabelText()
        checkbox=SimpleCheckbox(labelText="", a=a, classes=classes)
        ypCell.getPage(self.app.smwAccess)
        color="blue" if ypCell.status=="✅" else "red"
        link=f"<a href='{ypCell.pageUrl}' style='color:{color}'>{labelText}<a>"
        if ypCell.status=="ⓘ":
            link=f"{labelText}"
        # in a one column setting we need to break link and status message
        if "col-1" in classes:
            labelText=labelText.replace(":",":<br>")
            delim="<br>" 
        else:
            delim="&nbsp;"
        checkbox.label.inner_html=f"{link}{delim}{ypCell.statusMsg}"
        # link ypCell with Checkbox via a unique identifier
        ypCell.checkbox_id=uuid.uuid4()
        checkbox.data["ypcell_uuid"]=ypCell.checkbox_id
        self.ypcell_by_uuid[ypCell.checkbox_id]=ypCell
        self.checkbox_by_uuid[ypCell.checkbox_id]=checkbox
        return checkbox
      
    async def addRows(self,context:Context):
        """
        add the rows for the given topic
        """
        def updateProgress():
            percent=progress_steps/total_steps*100
            value=round(percent)
            self.app.progressBar.updateProgress(value)
       
        total_steps=0
        for topic_name,topic in context.topics.items():
            total_steps+=len(self.displayTargets())
            total_steps+=len(topic.properties)
        progress_steps=0
        updateProgress()
        for topic_name,topic in context.topics.items():
            self.checkboxes[topic_name]={}
            checkbox_row=self.checkboxes[topic_name]
            _topicRow=self.jp.Div(a=self.gridRows,classes="row",style='color:black')
            topicHeader=self.jp.Div(a=_topicRow,text=topic_name,classes=self.headerClasses,style=self.headerStyle)
            icon_url=f"{topic.iconUrl}" if topic.iconUrl.startswith("http") else f"{self.app.mw_context.wiki_url}{topic.iconUrl}"
            _topicIcon=self.jp.Img(src=icon_url, a=topicHeader,width=f'{self.iconSize}',height=f'{self.iconSize}')
            self.createSimpleCheckbox(labelText="→",title=f"select all {topic_name}",a=_topicRow,input=self.onSelectRowClick)
            for target in self.displayTargets():
                progress_steps+=1
                ypCell=YpCell.createYpCell(target=target, topic=topic)
                if len(ypCell.subCells)>0:
                    prop_div_col=self.jp.Div(a=_topicRow,classes=self.getCols(target))
                    prop_div=HideShow(a=prop_div_col,show_content=False,hide_show_label=("properties","properties"))
                    a=prop_div
                    classes=""
                else:
                    a=_topicRow 
                    classes="col-1"
                checkbox=self.createCheckBox(ypCell,a=a,classes=classes)
                checkbox_row[target.name]=(checkbox,ypCell)
                if len(ypCell.subCells)>0:
                    checkbox.on("input",self.onParentCheckboxClick)
                    for _prop_name,subCell in ypCell.subCells.items():
                        _subCheckBox=self.createCheckBox(subCell, a=prop_div,classes=classes)
                        progress_steps+=1
                        updateProgress()
                        await self.app.wp.update()
                updateProgress()
                await self.app.wp.update()
            pass
        # done
        self.app.progressBar.updateProgress(0)