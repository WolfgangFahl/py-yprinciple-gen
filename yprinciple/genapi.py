'''
Created on 2023-01-30

@author: wf
'''
from pathlib import Path
from meta.mw import SMWAccess
from meta.metamodel import Context
from yprinciple.smw_targets import SMWTarget
from yprinciple.ypcell import YpCell, MwGenResult, FileGenResult

class GeneratorAPI:
    """
    
    generator API e.g. to be used as a
    
    command line generator 
    """
    
    def __init__(self,verbose:bool=True,debug:bool=False):
        """
        constructor
        
        Args:
            verbose(bool): if True show verbose messages
            debug(bool): if True switch debugging on
        """
        self.verbose=verbose
        self.debug=debug
    
        
    @classmethod
    def fromArgs(cls,args)->"GeneratorAPI":
        """
        create a GeneratorAPI for the given command line arguments
        
        Args:
            args: command line arguments
            
        Returns:
            GeneratorAPI:
        """
        gen=GeneratorAPI(verbose=not args.quiet,debug=args.debug)
        gen.readContext(args.wikiId,args.context)
        return gen
       
    def readContext(self,wikiId:str,context_name:str):
        """
        Args:
            wikiId(str): the wikiId of the wiki to read the context from
            context_name: the name of the context to read
        """
        self.wikiId=wikiId
        self.smwAccess=SMWAccess(wikiId)
        self.mw_contexts=self.smwAccess.getMwContexts()
        self.mw_context=self.mw_contexts.get(context_name,None)
        self.context,self.error,self.errMsg=Context.fromWikiContext(self.mw_context, debug=self.debug)
      
    def filterTargets(self,target_names:list=None)->dict:
        """
        filter targets by a list of target_names
        
        Args:
            target_names(list): an optional list of target names
            
        Returns:
            dict: mapping from target names to targets
        """
        allTargets=SMWTarget.getSMWTargets()
        if target_names is None:
            targets=allTargets
        else:
            targets={}
            for target_name in target_names:
                if target_name in allTargets:
                    targets[target_name]=allTargets[target_name]
        return targets
    
    def yieldYpCells(self,hint:str,target_names:list=None,topic_names:list=None,with_subcells:bool=True):
        """
        generate/yield topics and targets via nested loop
        
        Args:
            hint(str): hint message to show how the yield is used
            with_subcells: if True yield sub cells (one level)
            target_name(list): if set filter targets by name
            topic_names(list): if set filter topics by name
        Returns:
            generator(YpCell)
        """
        def showMsg(topic_name:str,ypCell:YpCell):
            if self.verbose:
                target_name=ypCell.target.name
                print(f"generating {target_name} for {topic_name} {hint}...") 
            pass
              
        targets=self.filterTargets(target_names)
        for topic_name,topic in self.context.topics.items():
            # filter topic names
            if topic_names is not None and not topic_name in topic_names:
                continue
            for _target_name,target in targets.items():
                if target.showInGrid:
                    ypCell=YpCell.createYpCell(target=target, topic=topic)
                    if ypCell.target.is_multi:
                        if with_subcells:
                            for subCell in ypCell.subCells.values():
                                showMsg(topic_name,subCell)
                                yield subCell
                    else:
                        showMsg(topic_name,ypCell)
                        yield ypCell
                        
          
    def generateViaMwApi(self,target_names:list=None,topic_names:list=None,dryRun:bool=True,withEditor:bool=False):
        """
        start the generation via MediaWiki API
        
        Args:
            target_names(list): an optional list of target names
            topic_name(list): an optional list of topic names
            dryRun(bool): if True do not transfer results
            withEditor(bool): if True - start editor
            
        Return:
            list(MwGenResult): a list of Mediawiki Generator Results
        """
        self.smwAccess.wikiClient.login()
        genResults=[]
        for ypCell in self.yieldYpCells("via Mediawiki Api", target_names, topic_names):
            genResult=ypCell.generateViaMwApi(smwAccess=self.smwAccess,dryRun=dryRun,withEditor=withEditor)
            if self.debug or self.verbose:
                diff_url=genResult.getDiffUrl()
                diff_info="" if diff_url is None else diff_url
                diff_info+=f"({len(genResult.markup_diff)})"
                print(f"diff: {diff_info}")
            genResults.append(genResult)
        return genResults
 
    def generateToFile(self,target_dir=None,target_names:list=None,topic_names:list=None,dryRun:bool=True,withEditor:bool=False):
        """
        start the generation via MediaWiki Backup Directory
        
        Args:
            target_dir(str): the path to the target directory
            target_names(list): an optional list of target names
            topic_name(list): an optional list of topic names
            
            dryRun(bool): if True do not transfer results
            withEditor(bool): if True - start editor
            
        Return:
            list(FileGenResult): a list of File Generator Results
        """
        genResults=[]
        if target_dir is None:
            home = Path.home()
            target_dir=f"{home}/wikibackup/{self.wikiId}"
        for ypCell in self.yieldYpCells(f" to file in {target_dir}", target_names, topic_names):
            genResult=ypCell.generateToFile(target_dir=target_dir,dryRun=dryRun,withEditor=withEditor)
            genResults.append(genResult)
        return genResults
 
