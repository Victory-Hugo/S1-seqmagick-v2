"""
Split a FASTA file into per-record files / 按序列拆分 FASTA
"""
import logging
import os

from . import common

_LOG = logging.getLogger(__name__)


def build_parser(parser):
    parser.add_argument(
        'input_fasta', type=common.FileType('rt'),
        help="Input FASTA file / 输入 FASTA 文件")
    parser.add_argument(
        'output_dir',
        help="Output directory / 输出目录")


def _sanitize_header(header):
    header = header.strip()
    if not header:
        return 'unnamed'
    filename = header
    filename = filename.replace(os.sep, '_')
    if os.altsep:
        filename = filename.replace(os.altsep, '_')
    return filename


def _open_unique(path_base, seen_counts):
    count = seen_counts.get(path_base, 0) + 1
    seen_counts[path_base] = count
    if count == 1:
        return open(path_base, 'wt')
    path = "{0}.{1}".format(path_base, count)
    _LOG.warning("Duplicate header, writing to %s", path)
    return open(path, 'wt')


def action(arguments):
    common.exit_on_sigpipe()

    output_dir = arguments.output_dir
    os.makedirs(output_dir, exist_ok=True)

    current_out = None
    seen_counts = {}

    def close_current():
        nonlocal current_out
        if current_out is not None:
            current_out.close()
            current_out = None

    try:
        with arguments.input_fasta:
            for line in arguments.input_fasta:
                if line.startswith('>'):
                    close_current()
                    header = _sanitize_header(line[1:])
                    path_base = os.path.join(output_dir, header)
                    current_out = _open_unique(path_base, seen_counts)
                    current_out.write(line)
                    continue
                if current_out is None:
                    if line.strip():
                        raise ValueError("FASTA sequence found before header")
                    continue
                current_out.write(line)
    finally:
        close_current()
