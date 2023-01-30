'''
Created on 2023-01-30

@author: wf
'''
from meta.mw import SMWAccess
from meta.metamodel import Context
from yprinciple.smw_targets import SMWTarget
from yprinciple.ypcell import YpCell

class GeneratorBatch:
    """
    command line generator 
    """
    
    def __init__(self,args):
        """
        constructor
        """
        self.args=args
        self.debug=self.args.debug
        
    def start(self):
        """
        start the generation
        """
        self.smwAccess=SMWAccess(self.args.wikiId)
        self.mw_contexts=self.smwAccess.getMwContexts()
        self.mw_context=self.mw_contexts.get(self.args.context,None)
        context,error,errMsg=Context.fromWikiContext(self.mw_context, debug=self.args.debug)
        self.targets=SMWTarget.getSMWTargets()
        for topic_name,topic in context.topics.items():
            for target in self.targets:
                if target.showInGrid:
                    ypCell=YpCell.createYpCell(target=target, topic=topic)
                    withEditor=False
                    dryRun=True
                    ypCell.generate(smwAccess=self.smwAccess,dryRun=dryRun,withEditor=withEditor)
 
