"""
Modify sequence file(s) in place. / 原地修改序列文件
"""

import argparse
import logging

from . import convert, common


def build_parser(parser):
    """
    """
    convert.add_options(parser)

    parser.add_argument(
        'input_files', metavar="sequence_file", nargs=argparse.REMAINDER,
        type=str,
        help="Sequence file(s) to mogrify / 需要原地修改的序列文件")

    return parser


def action(arguments):
    """
    Run mogrify.  Most of the action is in convert, this just creates a temp
    file for the output.
    """
    input_paths = list(arguments.input_files or [])
    if not input_paths:
        raise ValueError("No input files provided")

    map_path = None
    if arguments.name_standard:
        if len(input_paths) < 2:
            raise ValueError("--name-standard requires a map file path")
        map_path = input_paths[-1]
        input_paths = input_paths[:-1]
        if len(input_paths) != 1:
            raise ValueError("--name-standard requires exactly one input file for mogrify")

    file_factory = common.FileType('rt')
    for input_path in input_paths:
        input_file = file_factory(input_path)
        logging.info(input_file)
        arguments.map_file = map_path
        # Generate a temporary file
        with common.atomic_write(
                input_file.name, file_factory=common.FileType('wt')) as tf:
            convert.transform_file(input_file, tf, arguments)
            if hasattr(input_file, 'close'):
                input_file.close()
