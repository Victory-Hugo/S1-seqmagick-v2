"""
Info action / 信息统计
"""

import collections
import csv
import itertools
import multiprocessing
import sys

from functools import partial

from Bio import SeqIO
from Bio.SeqUtils import ProtParam

from seqmagick2 import fileformat

from . import common

def build_parser(parser):
    parser.add_argument('source_files', metavar='sequence_files', nargs='+',
                        help="Input sequence files / 输入序列文件")
    parser.add_argument('--input-format', help="""Input format. Overrides
            extension for all input files / 输入格式，覆盖文件扩展名判断""")
    parser.add_argument('--out-file', dest='destination_file',
            type=common.FileType('wt'), default=sys.stdout,
            metavar='destination_file',
            help='Output destination. Default: STDOUT / 输出位置，默认 STDOUT')
    parser.add_argument('--format', dest='output_format',
        choices=('tab', 'csv', 'align'), help="""Specify output format as
        tab-delimited, CSV or aligned in a borderless table.  Default is
        tab-delimited if the output is directed to a file, aligned if output to
        the console. / 输出格式：tab、csv 或对齐文本表格。默认：写文件为 tab，输出到终端为对齐""")
    parser.add_argument('--threads', default=1,
            type=int,
            help="""Number of threads (CPUs). [%(default)s] / 线程数""")
    parser.add_argument('-more', '--more', dest='more', action='store_true',
            help="Output per-sequence details (length, GC%%, N count, gaps, "
                 "base counts, and protein properties when detected). / 输出每条序列详情")

class SeqInfoWriter(object):
    """
    Base writer for sequence files
    """

    def __init__(self, sequence_files, rows, output):
        self.sequence_files = sequence_files
        self.rows = rows
        self.output = output

    def write_row(self, row):
        raise NotImplementedError("Override in subclass")

    def write_header(self, header):
        self.write_row(header)

    def write(self):
        header = ('name', 'alignment', 'min_len', 'max_len', 'avg_len',
                  'num_seqs')

        self.write_header(header)

        for row in self.rows:
            self.write_row(_SeqFileInfo(*row))

class CsvSeqInfoWriter(SeqInfoWriter):
    delimiter = ','
    def __init__(self, sequence_files, rows, output):
        super(CsvSeqInfoWriter, self).__init__(sequence_files, rows, output)
        self.writer = csv.writer(self.output, delimiter=self.delimiter,
                lineterminator='\n')

    def write_row(self, row):
        # To cope with header
        if hasattr(row, '_replace'):
            row = row._replace(avg_len='{0:.2f}'.format(row.avg_len))
        self.writer.writerow(row)

class TsvSeqInfoWriter(CsvSeqInfoWriter):
    delimiter = '\t'

class AlignedSeqInfoWriter(SeqInfoWriter):
    def __init__(self, sequence_files, rows, output):
        super(AlignedSeqInfoWriter, self).__init__(sequence_files, rows, output)
        self.max_name_length = max(len(f) for f in self.sequence_files)

    def write_header(self, header):
        fmt = ('{0:' + str(self.max_name_length + 1) + 's}{1:10s}'
                '{2:>10s}{3:>10s}{4:>10s}{5:>10s}')
        print(fmt.format(*header), file=self.output)

    def write_row(self, row):
        fmt = ('{name:' + str(self.max_name_length + 1) + 's}{alignment:10s}'
                '{min_len:10d}{max_len:10d}{avg_len:10.2f}{num_seqs:10d}')
        print(fmt.format(**row._asdict()), file=self.output)

_WRITERS = {'csv': CsvSeqInfoWriter, 'tab': TsvSeqInfoWriter, 'align':
        AlignedSeqInfoWriter}

_HEADERS = ('name', 'alignment', 'min_len', 'max_len', 'avg_len',
              'num_seqs')
_SeqFileInfo = collections.namedtuple('SeqFileInfo', _HEADERS)

_DETAIL_HEADERS = ('file', 'id', 'length', 'gc_pct', 'n_count', 'gap_count',
                   'seq_type', 'a_count', 'c_count', 'g_count', 't_count',
                   'u_count', 'aa_pi', 'aa_gravy')
_DETAIL_HEADERS_NUC = ('file', 'id', 'length', 'gc_pct', 'n_count', 'gap_count',
                       'seq_type', 'a_count', 'c_count', 'g_count', 't_count',
                       'u_count')
_SeqRecordInfo = collections.namedtuple('SeqRecordInfo', _DETAIL_HEADERS)
_SeqRecordInfoNuc = collections.namedtuple('SeqRecordInfoNuc',
                                           _DETAIL_HEADERS_NUC)


class DetailSeqInfoWriter(SeqInfoWriter):
    def __init__(self, sequence_files, rows, output, headers=None):
        super(DetailSeqInfoWriter, self).__init__(sequence_files, rows, output)
        self.headers = headers or _DETAIL_HEADERS

    def write(self):
        self.write_header(self.headers)
        for row in self.rows:
            self.write_row(row)


class CsvDetailSeqInfoWriter(DetailSeqInfoWriter):
    delimiter = ','
    def __init__(self, sequence_files, rows, output, headers=None):
        super(CsvDetailSeqInfoWriter, self).__init__(
            sequence_files, rows, output, headers=headers)
        self.writer = csv.writer(self.output, delimiter=self.delimiter,
                lineterminator='\n')

    def write_row(self, row):
        if hasattr(row, '_replace'):
            updates = {}
            if 'gc_pct' in row._fields:
                updates['gc_pct'] = _format_optional_float(row.gc_pct)
            if 'aa_pi' in row._fields:
                updates['aa_pi'] = _format_optional_float(row.aa_pi)
            if 'aa_gravy' in row._fields:
                updates['aa_gravy'] = _format_optional_float(row.aa_gravy)
            for field in ('a_count', 'c_count', 'g_count', 't_count', 'u_count'):
                if field in row._fields:
                    updates[field] = _format_optional_int(getattr(row, field))
            if updates:
                row = row._replace(**updates)
        self.writer.writerow(row)


class TsvDetailSeqInfoWriter(CsvDetailSeqInfoWriter):
    delimiter = '\t'


class AlignedDetailSeqInfoWriter(DetailSeqInfoWriter):
    def __init__(self, sequence_files, rows, output, headers=None):
        super(AlignedDetailSeqInfoWriter, self).__init__(
            sequence_files, rows, output, headers=headers)
        self.file_width = max(len('file'), max(len(f) for f in sequence_files))
        self.id_width = max(len('id'), 20)
        self.include_protein = 'aa_pi' in self.headers

    def write_header(self, header):
        if self.include_protein:
            fmt = ('{0:' + str(self.file_width) + 's} '
                   '{1:' + str(self.id_width) + 's} '
                   '{2:>10s}{3:>10s}{4:>10s}{5:>10s}{6:>10s}'
                   '{7:>10s}{8:>10s}{9:>10s}{10:>10s}{11:>10s}'
                   '{12:>10s}{13:>10s}')
        else:
            fmt = ('{0:' + str(self.file_width) + 's} '
                   '{1:' + str(self.id_width) + 's} '
                   '{2:>10s}{3:>10s}{4:>10s}{5:>10s}{6:>10s}'
                   '{7:>10s}{8:>10s}{9:>10s}{10:>10s}{11:>10s}')
        print(fmt.format(*header), file=self.output)

    def write_row(self, row):
        data = row._asdict()
        data['gc_pct'] = _format_optional_float(row.gc_pct)
        data['a_count'] = _format_optional_int(row.a_count)
        data['c_count'] = _format_optional_int(row.c_count)
        data['g_count'] = _format_optional_int(row.g_count)
        data['t_count'] = _format_optional_int(row.t_count)
        data['u_count'] = _format_optional_int(row.u_count)
        if self.include_protein:
            data['aa_pi'] = _format_optional_float(row.aa_pi)
            data['aa_gravy'] = _format_optional_float(row.aa_gravy)
            fmt = ('{file:' + str(self.file_width) + 's} '
                   '{id:' + str(self.id_width) + 's} '
                   '{length:10d}{gc_pct:>10s}{n_count:10d}{gap_count:10d}'
                   '{seq_type:>10s}{a_count:>10s}{c_count:>10s}{g_count:>10s}'
                   '{t_count:>10s}{u_count:>10s}{aa_pi:>10s}{aa_gravy:>10s}')
        else:
            fmt = ('{file:' + str(self.file_width) + 's} '
                   '{id:' + str(self.id_width) + 's} '
                   '{length:10d}{gc_pct:>10s}{n_count:10d}{gap_count:10d}'
                   '{seq_type:>10s}{a_count:>10s}{c_count:>10s}{g_count:>10s}'
                   '{t_count:>10s}{u_count:>10s}')
        print(fmt.format(**data), file=self.output)


_DETAIL_WRITERS = {'csv': CsvDetailSeqInfoWriter, 'tab': TsvDetailSeqInfoWriter,
        'align': AlignedDetailSeqInfoWriter}

_DNA_CHARS = set('ACGTRYSWKMBDHVN')
_RNA_CHARS = set('ACGURYSWKMBDHVN')
_PROTEIN_CHARS = set('ACDEFGHIKLMNPQRSTVWYBJZXUO*')
_PROTEIN_CANONICAL = set('ACDEFGHIKLMNPQRSTVWY')

def _format_optional_float(value):
    if value is None:
        return ''
    return '{0:.2f}'.format(value)

def _format_optional_int(value):
    if value is None:
        return ''
    return str(value)

def _strip_protein_fields(row):
    return row[:-2]

def _detect_seq_type(seq):
    letters = set(seq)
    letters.discard('-')
    letters.discard('.')
    if not letters:
        return 'UNKNOWN'

    if letters <= _DNA_CHARS:
        return 'DNA'
    if letters <= _RNA_CHARS:
        if 'U' in letters and 'T' not in letters:
            return 'RNA'
        if 'T' in letters and 'U' not in letters:
            return 'DNA'
        return 'UNKNOWN'

    if letters <= _PROTEIN_CHARS:
        return 'PROTEIN'

    if letters - _DNA_CHARS and letters <= _PROTEIN_CHARS:
        return 'PROTEIN'

    return 'UNKNOWN'

def summarize_sequence_file(source_file, file_type=None):
    """
    Summarizes a sequence file, returning a tuple containing the name,
    whether the file is an alignment, minimum sequence length, maximum
    sequence length, average length, number of sequences.
    """
    is_alignment = True
    avg_length = None
    min_length = sys.maxsize
    max_length = 0
    sequence_count = 0

    # Get an iterator and analyze the data.
    with common.FileType('rt')(source_file) as fp:
        if not file_type:
            file_type = fileformat.from_handle(fp)
        for record in SeqIO.parse(fp, file_type):
            sequence_count += 1
            sequence_length = len(record)
            if max_length != 0:
                # If even one sequence is not the same length as the others,
                # we don't consider this an alignment.
                if sequence_length != max_length:
                    is_alignment = False

            # Lengths
            if sequence_length > max_length:
                max_length = sequence_length
            if sequence_length < min_length:
                min_length = sequence_length

            # Average length
            if sequence_count == 1:
                avg_length = float(sequence_length)
            else:
                avg_length = avg_length + ((sequence_length - avg_length) /
                                           sequence_count)

    # Handle an empty file:
    if avg_length is None:
        min_length = max_length = avg_length = 0
    if sequence_count <= 1:
        is_alignment = False

    return (source_file, str(is_alignment).upper(), min_length,
            max_length, avg_length, sequence_count)


def iter_sequence_details(source_file, file_type=None):
    with common.FileType('rt')(source_file) as fp:
        if not file_type:
            file_type = fileformat.from_handle(fp)
        for record in SeqIO.parse(fp, file_type):
            seq = str(record.seq).upper()
            length = len(record)
            gap_count = seq.count('-') + seq.count('.')
            n_count = seq.count('N')
            seq_type = _detect_seq_type(seq)

            if seq_type in ('DNA', 'RNA'):
                a_count = seq.count('A')
                c_count = seq.count('C')
                g_count = seq.count('G')
                t_count = seq.count('T')
                u_count = seq.count('U')
            else:
                a_count = c_count = g_count = t_count = u_count = None

            non_gap = length - gap_count
            if non_gap and seq_type in ('DNA', 'RNA'):
                gc_pct = ((g_count + c_count) / float(non_gap)) * 100.0
            else:
                gc_pct = None

            aa_pi = None
            aa_gravy = None
            if seq_type == 'PROTEIN':
                aa_seq = ''.join([aa for aa in seq if aa in _PROTEIN_CANONICAL])
                if aa_seq:
                    analysis = ProtParam.ProteinAnalysis(aa_seq)
                    aa_pi = analysis.isoelectric_point()
                    aa_gravy = analysis.gravy()

            yield (source_file, record.id, length, gc_pct, n_count, gap_count,
                   seq_type, a_count, c_count, g_count, t_count, u_count,
                   aa_pi, aa_gravy)

def action(arguments):
    """
    Given one more more sequence files, determine if the file is an alignment,
    the maximum sequence length and the total number of sequences.  Provides
    different output formats including tab (tab-delimited), csv and align
    (aligned as if part of a borderless table).
    """
    # Ignore SIGPIPE, for head support
    common.exit_on_sigpipe()
    common.exit_on_sigint()

    handle = arguments.destination_file
    output_format = arguments.output_format
    if not output_format:
        try:
            output_format = 'align' if handle.isatty() else 'tab'
        except AttributeError:
            output_format = 'tab'

    if arguments.more:
        writer_cls = _DETAIL_WRITERS[output_format]
        rows = (row for f in arguments.source_files
                for row in iter_sequence_details(
                    f, file_type=arguments.input_format))
        headers = _DETAIL_HEADERS_NUC
        try:
            first_row = next(rows)
        except StopIteration:
            rows = iter(())
        else:
            include_protein = first_row[6] == 'PROTEIN'
            if include_protein:
                headers = _DETAIL_HEADERS
                rows = itertools.chain([_SeqRecordInfo(*first_row)],
                                       (_SeqRecordInfo(*row) for row in rows))
            else:
                rows = itertools.chain([_SeqRecordInfoNuc(*_strip_protein_fields(first_row))],
                                       (_SeqRecordInfoNuc(*_strip_protein_fields(row))
                                        for row in rows))
    else:
        writer_cls = _WRITERS[output_format]
        ssf = partial(summarize_sequence_file, file_type=arguments.input_format)

        # if only one thread, do not use the multithreading so parent process
        # can be terminated using ctrl+c
        if arguments.threads > 1:
            pool = multiprocessing.Pool(processes=arguments.threads)
            rows = pool.imap(ssf, arguments.source_files)
        else:
            rows = (ssf(f) for f in arguments.source_files)

    with handle:
        if arguments.more:
            writer = writer_cls(arguments.source_files, rows, handle,
                                headers=headers)
        else:
            writer = writer_cls(arguments.source_files, rows, handle)
        writer.write()
