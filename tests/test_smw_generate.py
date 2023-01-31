'''
Created on 2023-01-18

@author: wf
'''
import os
from tests.basesmwtest import BaseSemanticMediawikiTest
from yprinciple.smw_targets import SMWTarget
from yprinciple.genapi import GeneratorAPI
from yprinciple.ypgen import YPGen
from yprinciple.ypcell import MwGenResult, FileGenResult

class TestSMWGenerate(BaseSemanticMediawikiTest):
    """
    test Semantic MediaWiki handling
    """
    
    def setUp(self, debug=False, profile=True):
        BaseSemanticMediawikiTest.setUp(self, debug=debug, profile=profile)
        for wikiId in ["cr"]:
            self.getWikiUser(wikiId, save=True)
            
    def getMarkup(self,debug:bool=False,topicNames=["Event"],target_keys=["category","concept","form","help","listOf","template"]):
        """
        get the markups for a given context, topicNames and target keys
        """
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
            
    def test_genbatch(self):
        """
        test the batch generator
        """
        parser=YPGen.getArgParser("YPGen automation test","No specific version - just testing")
        argv=[
            # uncomment to test a non dry run
            #"--noDry",
            "--wikiId","cr","--context","CrSchema","--topics","Event","--targets","help"]
        args = parser.parse_args(argv)
        gen=GeneratorAPI.fromArgs(args)
        self.assertIsNone(gen.error)
        self.assertIsNone(gen.errMsg)
        if not self.inPublicCI():
            genResults=gen.generateViaMwApi(args.targets, args.topics,dryRun=not args.noDry)
            self.assertTrue(len(genResults)==1)
            genResult=genResults[0]
            self.assertTrue(isinstance(genResult,MwGenResult))
        genResults=gen.generateToFile(target_dir="/tmp/ypgentest",target_names=args.targets,topic_names=args.topics,dryRun=False)
        self.assertTrue(len(genResults)==1)
        genResult=genResults[0]
        self.assertTrue(isinstance(genResult,FileGenResult))
        self.assertTrue("Help:Event.wiki" in genResult.path)
        self.assertTrue(os.path.isfile(genResult.path))