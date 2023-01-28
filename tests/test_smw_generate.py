'''
Created on 2023-01-18

@author: wf
'''
from tests.basesmwtest import BaseSemanticMediawikiTest
from yprinciple.smw_targets import SMWTarget

class TestSMWGenerate(BaseSemanticMediawikiTest):
    """
    test Semantic MediaWiki handling
    """
    
    def setUp(self, debug=False, profile=True):
        BaseSemanticMediawikiTest.setUp(self, debug=debug, profile=profile)
        for wikiId in ["cr"]:
            self.getWikiUser(wikiId, save=True)
            
    def getMarkup(self,debug:bool=False,topicNames=["Event"],target_keys=["category","concept","form","help","listOf","template"]):
        _smwAccess,context=self.getContext("cr", "CrSchema", debug)
        for topicname in topicNames:
            topic=context.topics[topicname]
            for target_key in target_keys:
                smwTarget=SMWTarget.getSMWTargets()[target_key]
                markup=smwTarget.generate(topic)
                yield topicname,target_key,smwTarget,markup
            
    def test_Issue13_ExternalIdentifer_Link_handling(self):
        """
        show Links for external Identifiers in templates
        https://github.com/WolfgangFahl/py-yprinciple-gen/issues/13
        """
        debug=self.debug
        debug=True
        for _topicname,_target_key,_smwTarget,markup in self.getMarkup(debug,target_keys=["template"]):
            if debug:
                print(markup)
            self.assertTrue("{{#show: {{PAGENAME}}|?Event wikidataid}}" in markup)
                
    def test_Issue12_TopicLink_handling(self):
        """
        test Topic link handling
        """
        debug=self.debug
        debug=True
        for topicname,target_key,smwTarget,markup in self.getMarkup(debug):
            if debug:
                print(markup)
                pass

