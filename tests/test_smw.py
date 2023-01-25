'''
Created on 2022-11-24

@author: wf
'''
from collections import Counter
from meta.mw import SMWAccess
from meta.metamodel import Context
from tests.basesmwtest import BaseSemanticMediawikiTest
from yprinciple.smw_targets import SMWTarget
from yprinciple.ypcell import YpCell

class TestSMW(BaseSemanticMediawikiTest):
    """
    test Semantic MediaWiki handling
    """
    
    def setUp(self, debug=False, profile=True):
        BaseSemanticMediawikiTest.setUp(self, debug=debug, profile=profile)
        for wikiId in ["wiki","ceur-ws","cr"]:
            self.getWikiUser(wikiId, save=True)
            
    def test_ypCell(self):
        """
        test ypCell
        """
        debug=True
        smwAccess=SMWAccess("ceur-ws",debug=debug)
        counter=Counter()
        for mw_context in smwAccess.getMwContexts().values():
            context,error,errMsg=Context.fromWikiContext(mw_context, debug=debug)
            self.assertIsNone(error)
            for target in SMWTarget.getSMWTargets().values():
                if not target.showInGrid:
                    continue
                for topic in context.topics.values():
                    ypCell=YpCell(modelElement=topic,target=target)
                    ypCell.getPage(smwAccess)
                    counter[ypCell.status]+=1
                    if debug:
                        print(f"{ypCell.getLabelText()}:{ypCell.statusMsg}")
                        print(ypCell.pageUrl)
        if debug:
            print(counter.most_common())
        self.assertTrue(counter["✅"]>=92)
        
    def testGenerate(self):
        """
        test the generate functionality
        """
        debug=self.debug
        debug=True
        smwAccess,context=self.getContext("cr", "CrSchema", debug)
        topic=context.topics["City"]
        withEditor=not self.inPublicCI()
        withEditor=False
        for target_key in ["category","concept","form","help","listOf","template","properties"]:
            smwTarget=SMWTarget.getSMWTargets()[target_key]
            ypCell=YpCell.createYpCell(target=smwTarget,topic=topic,debug=debug)
            markup_diff=ypCell.generate(smwAccess=smwAccess,dryRun=True,withEditor=withEditor)
            if markup_diff:
                diff_lines=markup_diff.split("\n")
                print(f"""found {len(diff_lines)} line differences for {ypCell.getPageTitle()}""")
                if self.debug:
                    print(markup_diff)       
                