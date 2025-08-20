"""
Created on 2022-11-24

@author: wf
"""

import sys
from argparse import ArgumentParser

from ngwidgets.cmd import WebserverCmd

from yprinciple.genapi import GeneratorAPI
from yprinciple.ypgenapp import YPGenServer


class YPGen(WebserverCmd):
    """
    Y-Principle Generator Command Line
    """

    def getArgParser(self, description: str, version_msg) -> ArgumentParser:
        """
        Setup command line argument parser

        Args:
            description (str): the description
            version_msg (str): the version message

        Returns:
            ArgumentParser: the argument parser
        """
        parser = super().getArgParser(description, version_msg)
        parser.add_argument(
            "--context",
            default="MetaModel",
            help="context to generate from [default: %(default)s]",
        )
        parser.add_argument(
            "--topics", nargs="*", help="list of topic names\n[default: %(default)s]"
        )
        parser.add_argument(
            "--targets", nargs="*", help="list of target names\n[default: %(default)s]"
        )
        parser.add_argument(
            "-ga",
            "--genViaMwApi",
            action="store_true",
            help="generate elements via Api",
        )
        parser.add_argument(
            "-gf", "--genToFile", action="store_true", help="generate elements to files"
        )
        parser.add_argument(
            "--targetPath",
            dest="targetPath",
            help="path for the files to be generated - uses wikibackup default path for wikiId if not specified",
            required=False,
        )
        parser.add_argument("--sidif", help="path to SiDIF input file")
        parser.add_argument(
            "-nd",
            "--noDry",
            action="store_true",
            help="switch off dry run [default: %(default)s]",
        )
        parser.add_argument(
            "--editor",
            action="store_true",
            help="open editor for results [default: %(default)s]",
        )
        parser.add_argument(
            "--push",
            action="store_true",
            help="push from source to target [default: %(default)s]",
        )
        parser.add_argument(
            "--wikiId",
            "--target",
            default="wiki",
            help="id of the wiki to generate for [default: %(default)s]",
        )
        parser.add_argument(
            "--source",
            default="profiwiki",
            help="id of the wiki to get concept and contexts (schemas) from [default: %(default)s]",
        )
        parser.add_argument(
            "--login",
            dest="login",
            action="store_true",
            help="login to source wiki for access permission",
        )
        return parser

    def handle_args(self,args):
        """
        work on the arguments
        """
        handled = super().handle_args(args)
        args = self.args
        if args.genToFile or args.genViaMwApi or args.push:
            gen = GeneratorAPI.fromArgs(args)
            if gen.error:
                print(f"{gen.errmsg}", file=sys.stderr)
                return 3
            dryRun = not args.noDry
            if not gen.context:
                msg=f"loading context {args.context} failed"
                print(f"{msg}", file=sys.stderr)
                return 4
            if args.genViaMwApi:
                gen.generateViaMwApi(
                    target_names=args.targets,
                    topic_names=args.topics,
                    dryRun=dryRun,
                    withEditor=args.editor,
                )
            if args.genToFile:
                gen.generateToFile(
                    target_dir=args.targetPath,
                    target_names=args.targets,
                    topic_names=args.topics,
                    dryRun=dryRun,
                    withEditor=args.editor,
                )
            if args.push:
                gen.push()
            handled = True
        return handled


def main(argv: list = None):
    """
    main call
    """
    cmd = YPGen(
        config=YPGenServer.get_config(),
        webserver_cls=YPGenServer,
    )
    exit_code = cmd.cmd_main(argv)
    return exit_code


DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
