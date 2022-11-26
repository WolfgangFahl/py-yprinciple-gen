'''
Created on 2022-11-24

@author: wf
'''
from collections import Counter
from meta.mw import SMWAccess
from meta.metamodel import Context
from tests.basemwtest import BaseMediawikiTest
from yprinciple.target import Target
from yprinciple.ypcell import YpCell

class TestSMW(BaseMediawikiTest):
    """
    test Semantic MediaWiki handling
    """
    
    def setUp(self, debug=False, profile=True):
        BaseMediawikiTest.setUp(self, debug=debug, profile=profile)
        for wikiId in ["wiki","ceur-ws"]:
            self.getWikiUser(wikiId, save=True)
            
    def test_ypCell(self):
        """
        test ypCell
        """
        debug=True
        smwAccess=SMWAccess("ceur-ws",debug=debug)
        counter=Counter()
        for mw_context in smwAccess.getMwContexts().values():
            context,error=Context.fromWikiContext(mw_context, debug=debug)
            self.assertIsNone(error)
            for target in Target.getSMWTargets():
                for topic in context.topics.values():
                    ypCell=YpCell(topic=topic,target=target)
                    pageText=ypCell.getPageText(smwAccess)
                    state=f"{len(pageText)}✅" if pageText else "❌"
                    if pageText:
                        counter["✅"]+=1
                    else:
                        counter["❌"]+=1
                    if debug:
                        print(f"{ypCell.getPageTitle()}:{state}")
        if debug:
            print(counter.most_common())
        self.asserTrue(counter["✅"]>=77)
        
    
         
    