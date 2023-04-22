'''
Created on 2023-01-30

@author: wf
'''
import traceback
import sys
from pathlib import Path
from meta.mw import SMWAccess
from meta.metamodel import Context
from yprinciple.smw_targets import SMWTarget
from yprinciple.ypcell import YpCell
from wikibot3rd.wikipush import WikiPush

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
        self.args=None
        
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
        gen.setWikiAndGetContexts(args)
        if args.sidif:
            gen.context,gen.error,gen.errMsg=Context.fromSiDIF_input(args.sidif, debug=args.debug)
        else:
            wikiId=args.source if args.push else args.wikiId
            gen.readContext(wikiId,args.context)
        # remember complete arguments (e.g. for push)
        gen.args=args
        return gen
    
    def setWikiAndGetContexts(self,args):
        """
        set my wiki and get Contexts for the given args
        
        Args:
            args: command line arguments
        """
        self.wikiId=args.wikiId
        self.smwAccess=SMWAccess(args.wikiId)
        self.smwSourceAccess=SMWAccess(args.source) if args.push else None
        self.smwContextAccess=self.smwSourceAccess if args.push else self.smwAccess
        self.mw_contexts=self.smwContextAccess.getMwContexts()
       
    def readContext(self,wikiId:str,context_name:str):
        """
        Args:
            wikiId(str): the wikiId of the wiki to read the context from
            context_name: the name of the context to read
        """
        self.mw_context=self.mw_contexts.get(context_name,None)
        if not self.mw_context:
            self.context=None
            self.errmsg=f"Could not read context {context_name} from {wikiId}"
            self.error=Exception(self.errmsg)
        else:    
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
            """
            show a message for the given topic_name
            
            Args:
                topic_name(str): topic
            """
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
                        
    def handleFailure(self,ypCell,ex):
        """
        handle the given failure
        """
        print(f"Warning ⚠️: generating {ypCell.target} for {ypCell.modelElement} failed with {str(ex)}",file=sys.stderr,flush=True)
        if self.debug:
            print(traceback.format_exc())
          
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
            try:
                genResult=ypCell.generateViaMwApi(smwAccess=self.smwAccess,dryRun=dryRun,withEditor=withEditor)
                if self.debug or self.verbose:
                    diff_url=genResult.getDiffUrl()
                    diff_info="" if diff_url is None else diff_url
                    diff_info+=f"({len(genResult.markup_diff)})"
                    print(f"diff: {diff_info}")
                genResults.append(genResult)
            except Exception as ex:
                self.handleFailure(ypCell, ex)
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
            try:
                genResult=ypCell.generateToFile(target_dir=target_dir,dryRun=dryRun,withEditor=withEditor)
                genResults.append(genResult)
            except Exception as ex:
                self.handleFailure(ypCell,ex)
        return genResults
    
    def push(self):
        """
        push according to my command line args
        """
        if not self.args.source:
            raise "missing source wiki"
        if self.args.topics:
            topic_names=self.args.topics
        else:
            topic_names=self.context.topics.keys()
        login=self.args.login
        force=self.args.force
        ignore=True
        fromWikiId=self.args.source
        wikiPush=WikiPush(fromWikiId=fromWikiId,toWikiId=self.smwAccess.wikiId,login=login,verbose=not self.args.quiet,debug=self.args.debug)
        if not self.args.quiet:
            print(f"pushing concept {self.args.context} from {self.args.source} to {self.wikiId} ...")
        all_page_titles=[]
        for topic_name in topic_names:
            topic=self.context.topics[topic_name]
            for page_titles,page_query,query_field in [
                    ([f"Concept:{topic_name}"],None,None),
                    ([f"Category:{topic_name}"],None,None),
                    ([f"Template:{topic_name}"],None,None),
                    ([f"Form:{topic_name}"],None,None),
                    ([f"Help:{topic_name}"],None,None),
                    ([f"List of {topic.pluralName}"],None,None),
                    (None,f"{{{{#ask: [[Property topic::Concept:{topic_name}]]|?#=page}}}}","page"),
                    (None,f"{{{{#ask: [[Topic name::{topic_name}]]|?Topic context=context}}}}","context")     
                ]:   
                if not page_titles:
                    page_titles=wikiPush.query(page_query, wiki=self.smwSourceAccess.wikiClient, queryField=query_field)
                all_page_titles.extend(page_title for page_title in page_titles if page_title not in all_page_titles)    
        failed=wikiPush.push(pageTitles=all_page_titles,force=force,ignore=ignore,withImages=True)
        if len(failed)>0:
            print(f"️Error {len(failed)} push attempts failed ❌️")
            for i,fail_name in enumerate(failed[:20]):
                print(f"    {i+1:2}: {fail_name} ❌") 
                