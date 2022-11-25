'''
Created on 2022-11-24

@author: wf
'''
from metamodel.mw import SMWAccess
from tests.basemwtest import BaseMediawikiTest

class TestSMW(BaseMediawikiTest):
    """
    test Semantic MediaWiki handling
    """
    
    def setUp(self, debug=False, profile=True):
        BaseMediawikiTest.setUp(self, debug=debug, profile=profile)
        for wikiId in ["wiki"]:
            self.getWikiUser(wikiId, save=True)
            
    
    def test_from_sididf(self):
        """
        test generating from SiDIF
        """
        
    
         
    