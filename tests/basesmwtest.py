'''
Created on 18.01.2023

@author: wf
'''
from tests.basemwtest import BaseMediawikiTest
from meta.mw import SMWAccess
from meta.metamodel import Context
import sys

class BaseSemanticMediawikiTest(BaseMediawikiTest):
    """
    special semantic mediawiki tests
    """
    
    def check_contexts(self,wikiId:str,ignoreExceptions:bool=True):
        """
        check the mediawiki contexts  for the given wikiId
        
        Args:
            wikiId(str): the wikiId to check
            ignoreExceptions(bool): if True only print out a warning other wise raise exception
        """
        mw_contexts={}
        try:
            smwAccess=SMWAccess(wikiId,debug=self.debug)
            mw_contexts=smwAccess.getMwContexts()
            for name,mw_context in mw_contexts.items():
                print(f"{name}: {mw_context.sidif_url()}")
            print (f"found {len(mw_contexts)} Contexts")
        except Exception as ex:
            print(f"warning Mediawiki context for {wikiId} fetching failed due to {str(ex)}",file=sys.stderr)
            if not ignoreExceptions:
                raise ex
        return smwAccess,mw_contexts
    
    def getContext(self,wikiId:str="wiki",context_name:str="MetaModel",debug:bool=False):
        """
        get the default meta model context
        """
        smwAccess,mw_contexts=self.check_contexts(wikiId)
        mw_context=mw_contexts[context_name]
        context,error,_errMsg=Context.fromWikiContext(mw_context, debug=debug)
        self.assertIsNone(error)
        return smwAccess,context    