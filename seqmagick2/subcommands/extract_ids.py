"""
Extract the sequence IDs from a file / 从文件中提取序列 ID
"""
import sys

from Bio import SeqIO

from seqmagick2 import fileformat

from . import common


def build_parser(parser):
    parser.add_argument(
        'sequence_file', type=common.FileType('rt'),
        help="Sequence file / 序列文件")
    parser.add_argument(
        '-o', '--output-file', type=common.FileType('wt'), default=sys.stdout,
        help="Destination file / 输出文件")
    parser.add_argument(
        '--input-format', help="Input format for sequence file / 输入序列文件格式")
    parser.add_argument(
        '-d', '--include-description', action='store_true', default=False,
        help='Include the sequence description in output [default: %(default)s] / 输出中包含描述信息')


def action(arguments):
    common.exit_on_sigpipe()

    # Determine file format for input and output
    source_format = (arguments.input_format or
                     fileformat.from_handle(arguments.sequence_file))

    with arguments.sequence_file:
        sequences = SeqIO.parse(arguments.sequence_file, source_format)
        if arguments.include_description:
            ids = (sequence.description for sequence in sequences)
        else:
            ids = (sequence.id for sequence in sequences)
        with arguments.output_file:
            for i in ids:
                print(i, file=arguments.output_file)
