'''
Created on 2022-11-26

@author: wf
'''
from yprinciple.target import Target

class SMWTarget(Target):
    @classmethod
    def getSMWTargets(cls):
        targets={
            "category": Target("Category","archive"),
            "concept": Target("Concept","puzzle"),
            "form": Target("Form","form-select"),
            "help": HelpTarget("Help","help-box"),
            "listOf": Target("List of","format-list-bulleted"),
            "template": Target("Template","file-document"),
            "properties": Target("Properties","alpha-p-circle",is_multi=True),
            "python": Target("Python","snake")
        }
        return targets
    
    def topicHeader(self,topic:'Topic')->str:
        """
        get the topic header for the given topic
        
        Args:
            topic(Topic): the topic to generate a header for
            
        Returns:
            str: the markup to be generated
        """
        markup=f"""{{{{#ask: [[Topic name::{topic.name}]]
|mainlabel=-
|?Topic icon = icon
|? = Topic
|?Topic name = name
|?Topic pluralName = pluralName
|?Topic documentation = documentation
}}}}
"""
        return markup
    
    def seealso(self,topic:'Topic')->str:
        """
        generate markup to to show relevant links for a topic
        """
        markup=f"""see also
* [[List of {topic.pluralName}]]
* [[Help:{topic.name}]]
* [[Concept:{topic.name}]]
* [[:Category:{topic.name}]]
* [[:Template:{topic.name}]]
* [[:Form:{topic.name}]] 
topic links:"""
        # @TODO fix
        """
        @for (TopicLink topicLink:topic.sourceTopicLinks.mTopicLinks) {
        @if (topicLink.targetTopic) {
        * [[:Category:@(topicLink.targetTopic.name)]]
        
        }"""
        return markup
        
    
    def uml(self,title:str,topic:'Topic')->str:
        """
        get the uml (plantuml) markup for  the given topic
        
        Args:
            topic(Topic): the topic to generate a header for
            
        Returns:
            str: the plantuml markup to be generated
        """
        markup=f"""=== {title} ===
<uml>
title @topic.name
note as @(topic.name)DiagramNote
Copyright (c) 2015-2022 BITPlan GmbH
[[http://www.bitplan.com]]
end note
note as {topic.name}Note
{topic.documentation}
end note
class {topic.name} {{
"""
        for prop in topic.properties.values():
            markup+=f"  {prop.type} {prop.name}\n"
        markup+=f"""}}"""
        # TODO TopicLinks
        """        
{topic.name}Note .. {topic.name}
@for (TopicLink topicLink:topic.sourceTopicLinks.mTopicLinks) {
@plantUmlRelation(topicLink)
}
@for (TopicLink topicLink:topic.targetTopicLinks.mTopicLinks) {
@plantUmlRelation(topicLink)
}
@bitplanumlci(12)"""
        markup+="""
</uml>"""
        return markup

class HelpTarget(SMWTarget):
    """
    a help Target
    """

    def generate(self,topic:'Topic')->str:
        """
        generate a result for the given topic
        
        see https://wiki.bitplan.com/index.php/SiDIFTemplates#help
        """
        markup=f"""[[File:Help_Icon.png|right]]
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
        """
}
@{
  ContextSetting contextSetting=ContextSetting.fromWikiTask(wikiTask);
}
@help(contextSetting.getMaintopic())
"""