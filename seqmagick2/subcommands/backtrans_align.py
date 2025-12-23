"""
Given a protein alignment and unaligned nucleotides, align the nucleotides
using the protein alignment. / 用蛋白比对结果指导核酸对齐

Protein and nucleotide sequence files must contain the same number of
sequences, in the same order, with the same IDs. / 蛋白与核酸序列数量、顺序、ID 必须一致
"""

import argparse
import sys

from seqmagick2 import pal2nal

from . import common


def build_parser(parser):
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
    parser.epilog = (
        "Common examples / 常用示例:\n"
        "  seqmagick2 backtrans-align protein.aln nuc.fasta -output fasta\n"
        "  seqmagick2 backtrans-align protein.aln nuc1.fasta nuc2.fasta -output clustal\n"
        "  seqmagick2 backtrans-align protein.aln nuc.fasta -output paml -codontable 2\n"
        "  seqmagick2 backtrans-align protein.aln nuc.fasta -nogap -nomismatch\n"
        "\n"
        "Codon tables / 密码子表:\n"
        "  1  Universal code / 通用密码子表\n"
        "  2  Vertebrate mitochondrial code / 脊椎动物线粒体\n"
        "  3  Yeast mitochondrial code / 酵母线粒体\n"
        "  4  Mold/Protozoan/Coelenterate mitochondrial & Mycoplasma/Spiroplasma\n"
        "     / 霉菌/原生动物/腔肠动物线粒体 与 支原体/螺旋体\n"
        "  5  Invertebrate mitochondrial / 无脊椎动物线粒体\n"
        "  6  Ciliate/Dasycladacean/Hexamita nuclear / 纤毛虫/伞藻/六鞭毛虫核\n"
        "  9  Echinoderm and Flatworm mitochondrial / 棘皮动物与扁形动物线粒体\n"
        " 10  Euplotid nuclear / 欧普洛特核\n"
        " 11  Bacterial/Archaeal/Plant plastid / 细菌/古菌/植物质体\n"
        " 12  Alternative yeast nuclear / 酵母核（替代表）\n"
        " 13  Ascidian mitochondrial / 海鞘线粒体\n"
        " 14  Alternative flatworm mitochondrial / 扁形动物线粒体（替代表）\n"
        " 15  Blepharisma nuclear / 纤毛虫 Blepharisma 核\n"
        " 16  Chlorophycean mitochondrial / 绿藻线粒体\n"
        " 21  Trematode mitochondrial / 吸虫线粒体\n"
        " 22  Scenedesmus obliquus mitochondrial / 斜生栅藻线粒体\n"
        " 23  Thraustochytrium mitochondrial / Thraustochytrium 线粒体\n"
    )
    parser.add_argument(
        'protein_align', type=common.FileType('r'),
        help='Protein Alignment / 蛋白比对文件')
    parser.add_argument(
        'nucl_align', nargs='+', type=common.FileType('r'),
        help='Nucleotide FASTA file(s) / 核酸序列文件（可多个）')
    parser.add_argument(
        '-o', '--out-file', type=common.FileType('w'),
        default=sys.stdout, metavar='destination_file',
        help='Output destination. Default: STDOUT / 输出位置')
    parser.add_argument(
        '-output', dest='outform',
        choices=('clustal', 'paml', 'fasta', 'codon'),
        default='clustal',
        help='Output format; default = clustal / 输出格式')
    parser.add_argument(
        '-blockonly', action='store_true',
        help='Show only user specified blocks / 仅输出指定区块')
    parser.add_argument(
        '-nogap', action='store_true',
        help='Remove columns with gaps and inframe stop codons / 移除含缺口或终止密码子的列')
    parser.add_argument(
        '-nomismatch', action='store_true',
        help='Remove mismatched codons / 移除不匹配密码子')
    parser.add_argument(
        '-codontable', type=int, choices=sorted(pal2nal.CODON_TABLES.keys()),
        default=1,
        help='Codon table number / 密码子表编号（见下方列表）')
    parser.add_argument(
        '-html', action='store_true',
        help='HTML output / HTML 输出')
    parser.add_argument(
        '-nostderr', action='store_true',
        help='No STDERR messages / 不输出 STDERR 提示')

    return parser


def action(arguments):
    common.exit_on_sigpipe()

    protein_path = arguments.protein_align.name
    nuc_paths = [n.name for n in arguments.nucl_align]
    try:
        pal2nal.run(protein_path, nuc_paths, arguments.out_file, sys.stderr, arguments)
    finally:
        if hasattr(arguments.protein_align, 'close'):
            arguments.protein_align.close()
        for handle in arguments.nucl_align:
            if hasattr(handle, 'close'):
                handle.close()
