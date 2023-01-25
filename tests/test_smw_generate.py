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

    def test_Issue12_TopicLink_handling(self):
        """
        test Topic link handling
        """
        debug=self.debug
        #debug=True
        _smwAccess,context=self.getContext("cr", "CrSchema", debug)
        for topicname in ["Event"]:
            topic=context.topics[topicname]
            for target_key in ["category","concept","form","help","listOf","template"]:
                smwTarget=SMWTarget.getSMWTargets()[target_key]
                markup=smwTarget.generate(topic)
                pass

