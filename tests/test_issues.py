'''
Created on 2024-10-31

@author: wf
'''
from tests.basesmwtest import BaseSemanticMediawikiTest
from yprinciple.smw_targets import SMWTarget

class TestIssues(BaseSemanticMediawikiTest):
    """
    test Semantic MediaWiki handling
    """

    def setUp(self, debug=False, profile=True):
        BaseSemanticMediawikiTest.setUp(self, debug=debug, profile=profile)
        contexts = {
            "contexts": ["CityContext"]
        }
        self.ccs = {}
        for wikiId, context_names in contexts.items():
            self.getWikiUser(wikiId, save=True)
            for context_name in context_names:
                self.ccs[f"{wikiId}-{context_name}"] = self.getContextContext(wikiId, context_name)

    def test_issue30_scoped_properties(self):
        """
        test
        scoped properties
        https://github.com/WolfgangFahl/pyMetaModel/issues/30
        """
        show=self.debug
        show=True
        cc = self.ccs["contexts-CityContext"]
        prop=cc.context.topics["City"].properties["Has Wikidata item ID"]
        smwTargets = SMWTarget.getSMWTargets()
        smwTarget= smwTargets.get("property")
        markup = smwTarget.generate(prop)
        if show:
            print(markup)