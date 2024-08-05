"""
Created on 2022-11-26

@author: wf
"""

from datetime import datetime

from meta.metamodel import Property, Topic, TopicLink

import yprinciple.ypcell as ypcell
from yprinciple.target import Target
from yprinciple.version import Version


class SMWTarget(Target):
    """
    a specialized generation target for Semantic MediaWiki
    """

    @classmethod
    def getSMWTargets(cls):
        """
        define the targets
        """
        targets = {
            "category": CategoryTarget("Category", "archive"),
            "concept": ConceptTarget("Concept", "extension"),
            "form": FormTarget("Form", "note_alt"),
            "help": HelpTarget("Help", "help_center"),
            "listOf": ListOfTarget("List of", "format_list_bulleted"),
            "template": TemplateTarget("Template", "description"),
            "properties": PropertyMultiTarget(
                "Properties", "local_parking", is_multi=True
            ),
            "property": PropertyTarget("Property", showInGrid=False),
            "python": PythonTarget("Python", "code"),
        }
        for target_key, target in targets.items():
            target.target_key = target_key
        targets["properties"].subTarget = targets["property"]
        return targets

    def i18n(self, text: str) -> str:
        """
        return the internationalized version of the given text

        Args:
            text (str): the text to internationalize

        Returns:
            str: the internationalized version of the text
        """
        # @TODO implement language support for non english wikis
        return text

    def topicHeader(self, topic: "Topic") -> str:
        """
        get the topic header for the given topic

        Args:
            topic (Topic): the topic to generate a header for

        Returns:
            str: the markup to be generated
        """
        markup = f"""{{{{#ask: [[Topic name::{topic.name}]]
|mainlabel=-
|?Topic icon = icon
|? = Topic
|?Topic name = name
|?Topic pluralName = pluralName
|?Topic documentation = documentation
}}}}
"""
        return markup

    def seealso(self, topic: Topic) -> str:
        """
        generate wiki markup to to show relevant links for a topic
        """
        markup = f"""see also
* [[List of {topic.pluralName}]]
* [[Help:{topic.name}]]
* [[Concept:{topic.name}]]
* [[:Category:{topic.name}]]
* [[:Template:{topic.name}]]
* [[:Form:{topic.name}]]
"""
        topicLinks = topic.targetTopicLinks.values()
        extends_topics=topic.get_extends_topics()
        if len(topicLinks)+len(extends_topics) > 0:
            markup += "related topics:\n" ""
            for extends_topic in extends_topics:
                markup += f"* [[Concept:{extends_topic.name}]]\n"
            for topicLink in topicLinks:
                markup += f"* [[Concept:{topicLink.targetTopic.name}]]\n"
        return markup

    def copyright(self) -> str:
        """
        get the copyright markup

        Returns:
            str: the copyright markup
        """
        currentYear = datetime.now().year
        markup = f"""<!--
  --     Copyright (C) 2015-{currentYear} BITPlan GmbH
  --
  --     Pater-Delp-Str. -- 1
  --     D-47877 -- Willich-Schiefbahn
  --
  --     http://www.bitplan.com
  --
  --
-->"""
        return markup

    def profiWiki(self) -> str:
        """
        markup for profiWiki
        """
        markup = (
            "[https://wiki.bitplan.com/index.php/ProfiWiki BITPlan Y-Prinzip ProfiWiki]"
        )
        return markup

    def bitplanumlci(self, fontSize: int = 12) -> str:
        """
        create plantuml skin params for BITPlan corporate identity

        Args:
            fontSize (int): the font size to use

        Returns:
            str: the wiki markup to be generated
        """
        currentYear = datetime.now().year
        markup = f"""' BITPlan Corporate identity skin params
' Copyright (c) 2015-{currentYear} BITPlan GmbH
' see https://wiki.bitplan.com/index.php/PlantUmlSkinParams#BITPlanCI
' skinparams generated by {Version.name}
"""
        skinparams = [
            "note",
            "component",
            "package",
            "usecase",
            "activity",
            "classAttribute",
            "interface",
            "class",
            "object",
        ]
        for skinparam in skinparams:
            markup += f"""skinparam {skinparam} {{
  BackGroundColor #FFFFFF
  FontSize {fontSize}
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}}
"""
        markup += """hide Circle
' end of skinparams '"""
        return markup

    def plantUmlRelation(self, topicLink: TopicLink) -> str:
        """
        generate wiki markup for a TopicLink/relation

        Args:
            topicLink (TopicLink): the topicLink to generate the relation for

        Returns:
            str: the wiki markup to generate
        """
        sourceMany = "*" if topicLink.sourceMultiple else "1"
        targetMany = "*" if topicLink.targetMultiple else "1"
        markup = f"""{topicLink.source} "{topicLink.sourceRole} ({sourceMany})" -- "{topicLink.targetRole}({targetMany})" {topicLink.target}\n"""
        return markup

    def plantUmlClass(self,topic: "Topic")->str:
        """
          get the plantuml markup for the given topic

          Args:
            topic (Topic): the topic to generate uml for

          Returns:
            str: the plantuml markup to be generated

        """
        markup=""
        extends=getattr(topic, "extends",None)
        extends_markup=f" extends {extends} " if extends else ""
        # recursive inheritance
        if extends:
            extends_topic=topic.context_obj.lookupTopic(extends,purpose=extends_markup)
            if extends_topic:
                markup+=self.plantUmlClass(extends_topic)

        markup += f"""note as {topic.name}Note
{topic.documentation}
end note
class {topic.name}{extends_markup} {{
"""
        for prop in topic.properties.values():
            prop_type = getattr(prop, "type", "Text")
            markup += f"  {prop_type} {prop.name}\n"
        markup += f"""}}
{topic.name}Note .. {topic.name}
"""
        # Relations/Topic Links
        for topicLink in topic.sourceTopicLinks.values():
            markup += f"{self.plantUmlRelation(topicLink)}"
        for topicLink in topic.targetTopicLinks.values():
            markup += f"{self.plantUmlRelation(topicLink)}"
        return markup

    def uml(self, title: str, topic: "Topic", output_format: str = "svg") -> str:
        """
        get the full uml (plantuml) markup for  the given topic

        Args:
            topic (Topic): the topic to generate uml for
            output_format (str): the output format to use - default: svg

        Returns:
            str: the plantuml markup to be generated

        """
        currentYear = datetime.now().year

        markup = f"""=== {title} ===
<uml format='{output_format}'>
title {topic.name}
note as {topic.name}DiagramNote
Copyright (c) 2015-{currentYear} BITPlan GmbH
[[http://www.bitplan.com]]
end note
"""
        markup+=self.plantUmlClass(topic)
        markup += f"""{self.bitplanumlci(12)}
</uml>"""
        return markup


class CategoryTarget(SMWTarget):
    """
    the target to generate "Category" pages

    see https://wiki.bitplan.com/index.php/SiDIFTemplates#category
    """

    def generate(self, topic: Topic) -> str:
        """
        generate a category page for the given topic

        e.g. https://wiki.bitplan.com/index.php/Category:Topic

        see https://wiki.bitplan.com/index.php/SiDIFTemplates#category

        Args:
            topic (Topic): the topic to generate wiki markup for

        Returns:
            str: the generated wiki markup
        """
        markup = f"""__NOTOC__
{{{{#ask: [[Topic name::{topic.name}]] | ?Topic wikiDocumentation= | mainlabel=-}}}}
{topic.getPluralName()} may be added and edited with the form [[Form:{topic.name}]]
* [[List of {topic.getPluralName()}]]
<div class="toccolours mw-collapsible mw-collapsed" style="width:1024px">
{topic.name} {self.i18n("description")}
<div class="mw-collapsible-content">
{self.uml("uml",topic)}
* [[Help:{topic.name}]]
* [[Concept:{topic.name}]]
* [[:Template:{topic.name}]]
* [[:Form:{topic.name}]]
=== Properties ===
"""
        for prop in topic.properties.values():
            markup += f"* [[Property:{topic.name} {prop.name}]]\n"
        markup += """</div>
</div>
"""
        if hasattr(topic, "extends") and topic.extends:
            markup+=f"""[[Category:{topic.extends}]]\n"""
        return markup


class ConceptTarget(SMWTarget):
    """
    the target to generate "Concept" pages

    see https://wiki.bitplan.com/index.php/SiDIFTemplates#concept
    """

    def generate(self, topic: "Topic") -> str:
        """
        generate a result for the given topic

        see https://wiki.bitplan.com/index.php/SiDIFTemplates#concept

        Args:
            topic(Topic): the topic to generate wiki markup for

        Returns:
            str: the generated wiki markup
        """
        extends_markup=f" extends {topic.extends} " if hasattr(topic,"extends") else ""
        markup = f"""{{{{Topic
|name={topic.name}
|pluralName={topic.getPluralName()}
|extends={extends_markup}
|icon={topic.icon}
|iconUrl={topic.iconUrl}
|documentation={topic.documentation}
|wikiDocumentation={topic.wikiDocumentation}
|defaultstoremode={topic.defaultstoremode}
|listLimit={topic.getListLimit()}
|cargo={getattr(topic,"cargo","false")}
|context={topic.context}
|storemode=property
}}}}
{{{{Topic
|viewmode=masterdetail
|storemode=none
}}}}
{{{{#forminput:form=Property|button text=add Property}}}}
=== Documentation ===
{topic.wikiDocumentation}
{self.uml("uml",topic)}

{{{{#concept:[[isA::{topic.name}]]
|{topic.wikiDocumentation}
{self.seealso(topic)}
}}}}
[[Category:{topic.name}]]
"""
        return markup


class HelpTarget(SMWTarget):
    """
    the help Target
    """

    def generate(self, topic: "Topic") -> str:
        """
        generate a result for the given topic

        see https://wiki.bitplan.com/index.php/SiDIFTemplates#help

        Args:
            topic (Topic): the topic to generate wiki markup for

        Returns:
            str: the generated wiki markup
        """
        markup = f"""[[File:Help_Icon.png|right]]
== Help for {topic.name} ==
{self.topicHeader(topic)}
=== Documentation ===
{topic.wikiDocumentation}
=== Example {topic.pluralName} ===
{{{{#ask: [[Concept:{topic.name}]]
}}}}
=== Properties ===
{{{{#ask: [[Concept:Property]][[Property topic::Concept:{topic.name}]]
| ?Property documentation = documentation
| ?Property type = type
| ?Property name = name
| ?Property label = label
| ?Property allowedValues = allowedValues
| ?Property mandatory = mandatory
| ?Property uploadable = uploadable
|format=table
}}}}
{self.uml("uml",topic)}
{self.seealso(topic)}
[[Category:{topic.name}]]
"""
        return markup


class FormTarget(SMWTarget):
    """
    the target to generate "Form" pages
    e.g. https://wiki.bitplan.com/index.php/Form:Topic

    see https://wiki.bitplan.com/index.php/SiDIFTemplates#form

    """

    def formTemplate(self, topic: Topic, isMultiple: bool):
        """
        create the SMW pagefomrs markups for the given topic

        Args:
            topic (Topic): the topic to create the markup for
            isMultiple (bool): True if there are multiple values allowed
        """
        multiple = "|multiple" if isMultiple else ""
        markup = f"""<div id="wikiPreview" style="display: none; padding-bottom: 25px; margin-bottom: 25px; border-bottom: 1px solid #AAAAAA;"></div>
{{{{{{section|{topic.name}|level=1|hidden}}}}}}
={topic.name}=
{{{{{{for template|{topic.name}{multiple}}}}}}}
{{| class="wikitable"
! colspan='2' | {topic.name}
|-
"""
        for prop in topic.propertiesByIndex():
            values_from_key = "values from="
            if prop.isLink:
                prop.values_from = f"{prop.topicLink.source}"
                prop.inputType = "dropdown"
                values_from_key = "values from concept="
                pass
            prop_type = getattr(prop, "type", "Text")
            markup += f"""! {prop.label}:
<!-- {prop_type} {prop.name} -->\n"""
            inputType = (
                f"|input type={prop.inputType}"
                if getattr(prop, "inputType", None)
                else ""
            )
            if "textarea" == getattr(prop, "inputType", None):
                inputType += "|editor=wikieditor"
            size = f"|size={prop.size}" if getattr(prop, "size", None) else ""
            mandatory = f"|mandatory" if getattr(prop, "mandatory", None) else ""
            uploadable = f"|uploadable" if getattr(prop, "uploadable", None) else ""
            size = f"|size={prop.size}" if getattr(prop, "size", None) else ""
            values_from = (
                f"|{values_from_key}{prop.values_from}"
                if getattr(prop, "values_from", None)
                else ""
            )
            defaultValue = (
                f"|default={prop.defaultValue}"
                if getattr(prop, "defaultValue", None)
                else ""
            )
            allowedValues = (
                f"|values={prop.allowedValues}"
                if getattr(prop, "allowedValues", None)
                else ""
            )
            markup += f"""|{{{{{{field|{prop.name}|property={topic.name} {prop.name}{inputType}{size}{mandatory}{uploadable}{values_from}{allowedValues}{defaultValue}}}}}}}
|-
"""
        markup += f"""|-
|}}
{{{{{{field|storemode|default={topic.defaultstoremode}|hidden}}}}}}
{{{{{{end template}}}}}}
<!-- {topic.name} -->
        """
        return markup

    def generate(self, topic: Topic) -> str:
        """
        generate the form page for the given topic

        Args:
            topic (Topic): the topic to generate wiki markup for

        Returns:
            str: the generated wiki markup
        """
        multiple = "subobject" == topic.defaultstoremode
        markup = f"""<noinclude>
This is the {self.profiWiki()}-Form for "{topic.name}".

Create a new {topic.name} by entering a new pagetitle for a {topic.name}
into the field below.

If you enter an existing {topic.name} pagetitle - you will edit the {topic.name}
with that pagetitle.
{{{{#forminput:form={topic.name}|values from concept={topic.name}}}}}

=== see also ===
{self.seealso(topic)}
</noinclude><includeonly>{self.formTemplate(topic,multiple)}

{{{{{{section|Freitext|level=1|hidden}}}}}}
=Freitext=
{{{{{{standard input|free text|rows=10}}}}}}

{{{{{{standard input|summary}}}}}}
{{{{{{standard input|changes}}}}}}

{{{{{{standard input|save}}}}}}
{{{{{{standard input|cancel}}}}}}
</includeonly>
        """
        return markup


class ListOfTarget(SMWTarget):
    """
    the target to generate "List of" pages
    e.g. https://wiki.bitplan.com/index.php/List_of_Topics

    see https://wiki.bitplan.com/index.php/SiDIFTemplates#listof

    """

    def getPageTitle(self, modelElement) -> str:
        pageTitle = f"List of {modelElement.pluralName}"
        return pageTitle

    def generate(self, topic: Topic) -> str:
        """
        generate the list of page for the given topic

        Args:
            topic (Topic): the topic to generate wiki markup for

        Returns:
            str: the generated wiki markup
        """
        markup = f"""__NOCACHE__
{self.topicHeader(topic)}
== {topic.getPluralName()} ==
{{{{#ask: [[Concept:{topic.name}]]|format=count}}}}
{{{{#forminput:form={topic.name}|button text=add {topic.name}}}}}
{topic.askQuery()}
[[:Category:{topic.name}]]
    """
        return markup


class TemplateTarget(SMWTarget):
    """
    the template Target
    """

    def generateTopicCall(self,topic:Topic)->str:
        """
        generate the markup for the template call of the given topic

        Args:
            topic (Topic): the topic to generate wiki markup for
        """
        markup=f"""{{{{{topic.name}\n"""
        for prop in topic.properties.values():
            markup+=f"""|{prop.name}={{{{{{{prop.name}|}}}}}}\n"""
        markup+="""|storemode={{{storemode|}}}
|viewmode={{{viewmode|}}}
}}"""
        return markup

    def generate(self, topic: Topic) -> str:
        """
        generate a template for the given topic

        see https://wiki.bitplan.com/index.php/SiDIFTemplates#template

        Args:
            topic (Topic): the topic to generate wiki markup for

        Returns:
            str: the generated wiki markup
        """
        markup = f"""<noinclude>{self.copyright()}
This is the {self.profiWiki()}-Template for "{topic.name}".
=== see also ===
{self.seealso(topic)}
=== Usage ===
<pre>{{{{{topic.name}
"""
        all_properties=topic.get_all_properties()
        for prop in all_properties:
            markup += f"|{prop.name}=\n"
        markup += f"""|storemode=property or subobject or none"
}}}}
</pre>
[[Category:Template]]
</noinclude><includeonly>"""
        extends_topics=topic.get_extends_topics()
        for extends_topic in extends_topics:
            markup+=self.generateTopicCall(extends_topic)
        markup+=f"""{{{{#switch:{{{{{{storemode|}}}}}}
|none=
|subobject={{{{#subobject:-
|isA={topic.name}
"""
        for prop in topic.properties.values():
            markup += f"|{topic.name} {prop.name}={{{{{{{prop.name}|}}}}}}\n"
        markup += f"""}}}}
|#default={{{{#set:
|isA={topic.name}
"""
        for prop in topic.properties.values():
            # separator handling
            sep = ""
            if prop.isLink:
                tl = prop.topicLink
                if hasattr(tl, "separator"):
                    sep = f"|+sep={tl.separator}"
            markup += f"|{topic.name} {prop.name}={{{{{{{prop.name}|}}}}}}{sep}\n"
        markup += f"""}}}}\n"""  # end of #set
        markup += f"""}}}}\n"""  # end of #switch
        markup += f"""{{{{#switch:{{{{{{viewmode|}}}}}}"""
        markup += "|hidden="
        markup += "|masterdetail=\n"
        for topicLink in topic.sourceTopicLinks.values():
            if topicLink.targetTopic:
                markup += f"= {topicLink.targetRole} =\n"
                markup += f"{{{{#ask:[[Concept:{topicLink.targetTopic.name}]]"
                markup += f"[[{topicLink.targetTopic.name} {topicLink.sourceRole}::{{{{FULLPAGENAME}}}}]]\n"
                for prop in topicLink.targetTopic.propertiesByIndex():
                    markup += (
                        f"| ?{topicLink.targetTopic.name} {prop.name} = {prop.name}\n"
                    )
                    pass
                markup += f"}}}}"  # end #ask
                pass
        markup += "|#default="
        markup += f"""{{{{{{!}}}} class='wikitable'
! colspan='2' {{{{!}}}}{topic.name}
{{{{!}}}}-
{{{{#switch:{{{{{{storemode|}}}}}}|property=
! colspan='2' style='text-align:left' {{{{!}}}} {{{{Icon|name=edit|size=24}}}}{{{{Link|target=Special:FormEdit/{topic.name}/{{{{FULLPAGENAME}}}}|title=edit}}}}
{{{{!}}}}-
}}}}
"""
        for prop in topic.properties.values():
            # https://github.com/WolfgangFahl/py-yprinciple-gen/issues/13
            # show Links for external Identifiers in templates
            prop_type = getattr(prop, "type", "Text")
            if prop_type == "External identifier" or prop.isLink:
                link_markup = (
                    "→{{#show: {{FULLPAGENAME}}|" + f"?{topic.name} {prop.name}" + "}}"
                )
                pass
            elif prop_type == "Page":
                link_markup = f"→[[{{{{{{{prop.name}|}}}}}}]]"
            else:
                link_markup = ""
            markup += f"""![[Property:{topic.name} {prop.name}|{prop.name}]]
{{{{!}}}}&nbsp;{{{{#if:{{{{{{{prop.name}|}}}}}}|{{{{{{{prop.name}}}}}}}|}}}}{link_markup}
{{{{!}}}}-\n"""
        markup += f"{{{{!}}}}}}\n"  # end of table
        markup += f"""}}}}\n"""  # end of #switch viewmode

        if hasattr(topic, "defaultstoremode"):
            if topic.defaultstoremode == "property":
                markup += (
                    f"[[Category:{topic.name}]]{{{{#default_form:{topic.name}}}}}\n"
                )

        markup += """</includeonly>"""
        return markup


class PropertyMultiTarget(SMWTarget):
    """
    the Property Multi Target
    """

    def addSubCells(self, ypCell: "ypcell.YpCell", topic: Topic, debug: bool = False):
        """
        add the subcells for the given ypCell and topic

        Args:
            ypCell: the ypCell
            topic (Topic): the topic to add subcells for
        """
        for prop in topic.properties.values():
            subCell = ypcell.YpCell(
                modelElement=prop, target=self.subTarget, debug=debug
            )
            ypCell.subCells[prop.name] = subCell


class PropertyTarget(SMWTarget):
    """
    the Property Target
    """

    def getPageTitle(self, prop) -> str:
        """
        get the page title for the given property

        Args:
            prop: the Property to get the page title for

        Returns:
            str: the markup
        """
        pageTitle = f"{self.name}:{prop.topic} {prop.name}"
        return pageTitle

    def generate(self, prop: Property) -> str:
        """
        generate wiki markup for the given property

        see https://wiki.bitplan.com/index.php/SiDIFTemplates#propertiesdefs

        Returns:
            str: the wiki markup for the given property
        """
        topic_name = prop.topic
        topicWithConcept = f"Concept:{topic_name}"
        markup = f"""{{{{Property
|name={prop.name}
|label={prop.label}
        """
        if hasattr(prop, "documentation"):
            markup += f"""|documentation={prop.documentation}\n"""
        prop_type = getattr(prop, "type", "Text")
        markup += f"""|type=Special:Types/{prop_type}
"""
        # @TODO read from metamodel
        for prop_name in [
            "index",
            "sortPos",
            "primaryKey",
            "mandatory",
            "namespace",
            "size",
            "uploadable",
            "defaultValue",
            "inputType",
            "allowedValues",
            "values_from",
            "formatterURI",
            "showInGrid",
            "isLink",
        ]:
            if hasattr(prop, prop_name):
                value = getattr(prop, prop_name, None)
                if value is not None:
                    markup += f"|{prop_name}={value}\n"
                    # e.g. |index={prop.index}
        markup += f"""|topic={(topicWithConcept)}
|storemode=prop
}}}}
* [[Has type::{prop.type}]]
"""
        if hasattr(prop, "formatterURI"):
            markup += f"""* External formatter uri: [[External formatter uri::{prop.formatterURI}]]
"""
        markup += f"""
This is a Property with type {{{{#show: {{{{FULLPAGENAMEE}}}} | ?Property type#- }}}}
"""
        return markup


class PythonTarget(SMWTarget):
    """
    generator for Python Code for a Topic
    """

    def pythonPropType(self, prop: Property) -> str:
        """
        get the python property type for the given Property
        """
        ptype = "str"
        typestr = prop.type
        typestr = typestr.replace("Types/", "")
        if typestr == "Boolean":
            ptype = "bool"
        elif typestr == "Number":
            ptype = "float"
        return ptype

    def generate(self, topic: "Topic") -> str:
        """
        generate python code for the given topic
        """
        markup = f'''from dataclasses import dataclass
from typing import Optional
import dacite
@dataclass
class {topic.name}:
    """
    {topic.documentation}
    """
    pageTitle:str
'''

        for prop in topic.propertiesByIndex():
            markup += f"""    {prop.name}:Optional[{self.pythonPropType(prop)}] # {getattr(prop,"documentation","")}\n"""
        markup += f'''
    @classmethod
    def askQuery(cls):
        """
        get the ask Query for {topic.name}

        Returns:
            str: the mediawiki markup for the ask query
        """
        ask="""{topic.askQuery(mainlabel="pageTitle",filterShowInGrid=False,listLimit=10000)}"""
        return ask

    @classmethod
    def fromDict(cls,data:dict):
        """
        create a {topic.name} from the given dict

        Args:
            data(dict): the dict to create the {topic.name} from

        Returns:
            {topic.name}: the freshly created {topic.name}
        """
        {topic.name.lower()}=dacite.from_dict(data_class=cls,data=data)
        return {topic.name.lower()}
        '''

        return markup
