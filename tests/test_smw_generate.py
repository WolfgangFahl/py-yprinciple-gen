"""
Created on 2023-01-18

@author: wf
"""

import os

from tests.basesmwtest import BaseSemanticMediawikiTest
from yprinciple.genapi import GeneratorAPI
from yprinciple.ypcell import FileGenResult, MwGenResult
from yprinciple.ypgen import YPGen
from yprinciple.ypgenapp import YPGenServer
from yprinciple.smw_targets import SMWTarget

class TestSMWGenerate(BaseSemanticMediawikiTest):
    """
    test Semantic MediaWiki handling
    """

    def setUp(self, debug=False, profile=True):
        BaseSemanticMediawikiTest.setUp(self, debug=debug, profile=profile)
        contexts = {
            "cr": ["CrSchema",
                   "CrSchema24-08"
                   ],
            "wiki": ["MetaModel"],
            "contexts": ["CityContext"]
        }
        self.ccs = {}
        for wikiId, context_names in contexts.items():
            self.getWikiUser(wikiId, save=True)
            for context_name in context_names:
                self.ccs[f"{wikiId}-{context_name}"] = self.getContextContext(wikiId, context_name)

    def testTargets(self):
        """
        test the potential targets
        """
        targets=SMWTarget.getSMWTargets()
        debug=self.debug
        if debug:
            print(targets.keys())
        self.assertTrue("listOf" in targets)

    def testInheritance(self):
        """
        test inheritance
        """
        show = self.debug
        #show=True
        cc = self.ccs["cr-CrSchema24-08"]
        for gr in cc.get_markup(
            topic_names=["Event"], target_keys=["concept"], show=show
        ):
            self.assertTrue("Event extends" in gr.markup)
            pass

    def testTemplate(self):
        """
        test the template handling
        """
        show = self.debug
        # show=True
        cc = self.ccs["cr-CrSchema"]
        for gr in cc.get_markup(
            topic_names=["Event"], target_keys=["template"], show=show
        ):
            self.assertTrue(
                "</pre>" in gr.markup
            )

    def test_Issue13_ExternalIdentifer_Link_handling(self):
        """
        show Links for external Identifiers in templates
        https://github.com/WolfgangFahl/py-yprinciple-gen/issues/13
        """
        show = self.debug
        # show=True
        cc = self.ccs["cr-CrSchema"]
        for gr in cc.get_markup(
            topic_names=["Event"], target_keys=["template"], show=show
        ):
            self.assertTrue(
                "{{#show: {{FULLPAGENAME}}|?Event wikidataid}}" in gr.markup
            )

    def test_Issue12_TopicLink_handling(self):
        """
        test Topic link handling
        """
        show = self.debug
        # show=True
        cc = self.ccs["cr-CrSchema"]
        for gr in cc.get_markup(topic_names=["Event"], target_keys=["form"], show=show):
            expected = "{{{field|city|property=Event city|input type=dropdown|values from concept=City}}}"
            self.assertTrue(expected in gr.markup)

    def test_Issue28_viewmode_masterdetail(self):
        """
        test master/detail viewmode generation and TopicLink separator

        https://github.com/WolfgangFahl/py-yprinciple-gen/issues/28
        refactor viewmode "masterdetail"

        """
        cc = self.ccs["wiki-MetaModel"]
        show = self.debug
        #show = True
        for gr in cc.get_markup(
            topic_names=["Context"], target_keys=["template"], show=show
        ):
            expected_parts = [
                "= topics =",
                "{{#ask:[[Concept:Topic]][[Topic context::{{FULLPAGENAME}}]]",
            ]
            for expected in expected_parts:
                self.assertTrue(expected in gr.markup)

    def test_Issue29_TopicLink_separator(self):
        """
        https://github.com/WolfgangFahl/py-yprinciple-gen/issues/29
        1:N relation using TopicLink separator

        """
        cc = self.ccs["cr-CrSchema"]
        show = self.debug
        show=True
        for gr in cc.get_markup(
            topic_names=["Paper"], target_keys=["template"], show=show
        ):
            expected_parts = [
                "|Paper authors={{{authors|}}}|+sep=,",
                "{{!}}&nbsp;{{#if:{{{authors|}}}|{{{authors}}}|}}→{{#show: {{FULLPAGENAME}}|?Paper authors}}",
            ]
            for expected in expected_parts:
                self.assertTrue(expected in gr.markup)

    def test_genbatch(self):
        """
        test the batch generator
        """
        cmd = YPGen(
            config=YPGenServer.get_config(),
            webserver_cls=YPGenServer,
        )
        parser = cmd.getArgParser(
            "YPGen automation test", "No specific version - just testing"
        )
        argv = [
            # uncomment to test a non dry run
            # "--noDry",
            "--wikiId",
            "cr",
            "--context",
            "CrSchema",
            "--topics",
            "Event",
            "--targets",
            "help",
        ]
        args = parser.parse_args(argv)
        gen = GeneratorAPI.fromArgs(args)
        self.assertIsNone(gen.error)
        self.assertIsNone(gen.errmsg)
        if not self.inPublicCI():
            genResults = gen.generateViaMwApi(
                args.targets, args.topics, dryRun=not args.noDry
            )
            self.assertTrue(len(genResults) == 1)
            genResult = genResults[0]
            self.assertTrue(isinstance(genResult, MwGenResult))
        genResults = gen.generateToFile(
            target_dir="/tmp/ypgentest",
            target_names=args.targets,
            topic_names=args.topics,
            dryRun=False,
        )
        self.assertTrue(len(genResults) == 1)
        genResult = genResults[0]
        self.assertTrue(isinstance(genResult, FileGenResult))
        self.assertTrue("Help:Event.wiki" in genResult.path)
        self.assertTrue(os.path.isfile(genResult.path))
