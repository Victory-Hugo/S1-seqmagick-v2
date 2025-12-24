#! /usr/bin/env python

import argparse
import logging
import os
import sys
from functools import partial

from seqmagick2 import __version__ as version
from seqmagick2 import subcommands

_COLOR_RESET = '\033[0m'
_COLOR_MAP = {
    logging.DEBUG: '\033[36m',
    logging.INFO: '\033[32m',
    logging.WARNING: '\033[33m',
    logging.ERROR: '\033[31m',
    logging.CRITICAL: '\033[41m',
}
_COLOR_USAGE = '\033[33m'
_COLOR_SECTION = '\033[36m'
_COLOR_OPTIONAL = '\033[32m'
_COLOR_POSITIONAL = '\033[35m'
_COLOR_TEXT = '\033[37m'


class _ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, use_color):
        super(_ColoredFormatter, self).__init__(fmt)
        self.use_color = use_color

    def format(self, record):
        msg = super(_ColoredFormatter, self).format(record)
        if not self.use_color:
            return msg
        color = _COLOR_MAP.get(record.levelno)
        if not color:
            return msg
        return color + msg + _COLOR_RESET


class _ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, *args, **kwargs):
        self.use_color = kwargs.pop('use_color', False)
        super(_ColoredHelpFormatter, self).__init__(*args, **kwargs)

    def _wrap_color(self, text, color):
        if not self.use_color or not text:
            return text
        return color + text + _COLOR_RESET

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'usage: '
        if self.use_color:
            prefix = self._wrap_color(prefix.rstrip(), _COLOR_USAGE) + ' '
        return super(_ColoredHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)

    def start_section(self, heading):
        heading = self._wrap_color(heading, _COLOR_SECTION)
        super(_ColoredHelpFormatter, self).start_section(heading)

    def add_text(self, text):
        if text:
            text = self._wrap_color(text, _COLOR_TEXT)
        super(_ColoredHelpFormatter, self).add_text(text)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            invocation = super(_ColoredHelpFormatter, self)._format_action_invocation(action)
            return self._wrap_color(invocation, _COLOR_POSITIONAL)
        opts = ', '.join(action.option_strings)
        if action.nargs != 0:
            default = self._get_default_metavar_for_optional(action)
            opts += ' ' + self._format_args(action, default)
        return self._wrap_color(opts, _COLOR_OPTIONAL)


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
    use_color = sys.stderr.isatty() and not bool(os.environ.get('NO_COLOR'))
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(_ColoredFormatter(logformat, use_color))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(loglevel)

    return action(arguments)


def parse_arguments(argv):
    """
    Extract command-line arguments for different actions.
    """
    use_color_help = sys.stdout.isatty() and not bool(os.environ.get('NO_COLOR'))
    parser = argparse.ArgumentParser(
        description='seqmagick2 - Manipulate sequence files. / 序列文件处理工具。',
        prog='seqmagick2',
        epilog=(
            "Most common examples / 常用示例:\n"
            "  seqmagick2 info --more input.fasta # 显示序列信息\n"
            "  seqmagick2 convert input.fasta output.phy # 将 fasta 转换为 phy 格式\n"
            "  seqmagick2 convert --rename map.tsv input.fasta output.fasta # 根据 map.tsv 对序列重命名\n"
            "  seqmagick2 convert --cut=1:300 --line-wrap 0 input.fasta output.fasta # 保留第 1号位置 到 300 的序列，不分行\n"
            "  seqmagick2 convert --deduplicate-sequences input.fasta output.fasta # 删除重复序列\n"
            "  seqmagick2 convert --include-from-file List_ID.txt input.fasta output.fasta # 仅保留 List_ID.txt 中的序列\n"
            "  seqmagick2 split input.fasta output_dir/ # 将序列拆分为多个文件，保存在 output_dir/\n"
            
        ),
        formatter_class=partial(_ColoredHelpFormatter, use_color=use_color_help))

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
        subparser = subparsers.add_parser(
            name,
            help=mod.__doc__,
            description=mod.__doc__,
            formatter_class=partial(_ColoredHelpFormatter,
                                    use_color=use_color_help))
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
