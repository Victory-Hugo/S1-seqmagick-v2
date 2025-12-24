#! /usr/bin/env python

import argparse
import logging
import sys

from seqmagick2 import __version__ as version
from seqmagick2 import subcommands


def main(argv=sys.argv[1:]):
    action, arguments = parse_arguments(argv)

    loglevel = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }.get(arguments.verbosity, logging.DEBUG)

    if arguments.verbosity > 1:
        logformat = '%(levelname)s %(module)s %(lineno)s %(message)s'
    else:
        logformat = '%(message)s'

    # set up logging
    logging.basicConfig(stream=sys.stderr, format=logformat, level=loglevel)

    return action(arguments)


def parse_arguments(argv):
    """
    Extract command-line arguments for different actions.
    """
    parser = argparse.ArgumentParser(
        description='seqmagick2 - Manipulate sequence files. / 序列文件处理工具。',
        prog='seqmagick2',
        epilog=(
            "Most common examples / 常用示例:\n"
            "  seqmagick2 convert input.fasta output.phy # 将 fasta 转换为 phy 格式\n"
            "  seqmagick2 convert --rename map.tsv input.fasta output.fasta # 根据 map.tsv 对序列重命名\n"
            "  seqmagick2 convert --cut=1:300 input.fasta output.fasta # 保留第 1号位置 到 300 的序列\n"
            "  seqmagick2 convert --deduplicate-sequences input.fasta output.fasta # 删除重复序列\n"
            "  seqmagick2 info --more input.fasta # 显示序列信息\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-V', '--version', action='version',
            version='seqmagick2 v' + version,
            help="Print the version number and exit / 打印版本号后退出")
    parser.add_argument('-v', '--verbose', dest='verbosity',
            action='count', default=1,
            help="Be more verbose. Specify -vv or -vvv for even more / "
                 "更详细输出，可使用 -vv 或 -vvv")
    parser.add_argument('-q', '--quiet', action='store_const', const=0,
            dest='verbosity', help="Suppress output / 静默输出")

    # Subparsers
    subparsers = parser.add_subparsers(dest='subparser_name')

    parser_help = subparsers.add_parser(
        'help',
        help='Detailed help for actions using help <action> / 使用 help <action> 查看详细说明')

    parser_help.add_argument('action')

    # Add actions
    actions = {}
    for name, mod in subcommands.itermodules():
        subparser = subparsers.add_parser(name, help=mod.__doc__,
                description=mod.__doc__)
        mod.build_parser(subparser)
        actions[name] = mod.action

    arguments = parser.parse_args(argv)
    arguments.argv = argv
    action = arguments.subparser_name

    if action is None:
        parse_arguments(['-h'])
    if action == 'help':
        return parse_arguments([str(arguments.action), '-h'])

    return actions[action], arguments


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
