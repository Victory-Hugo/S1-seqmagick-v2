"""
Use termal to view the MSA sequence in terminal. / 使用 termal软件在终端查看多序列对齐文件。
"""

import argparse
import os
import stat
import subprocess
import sys


def build_parser(parser):
    parser.add_argument(
        'msa_file',
        help="MSA file to view / 需要查看的多序列对齐文件")


def _termal_executable():
    package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    project_root = os.path.abspath(os.path.join(package_root, '..'))
    candidate_bins = [
        os.path.join(package_root, 'bin'),
        os.path.join(project_root, 'bin'),
    ]
    if sys.platform.startswith('win'):
        exe_name = 'termal_win.exe'
    elif sys.platform == 'darwin':
        exe_name = 'termal_apple'
    else:
        exe_name = 'termal_linux'
    exe_path = None
    for bin_dir in candidate_bins:
        candidate = os.path.join(bin_dir, exe_name)
        if os.path.exists(candidate):
            exe_path = candidate
            break
    if exe_path is None:
        exe_path = os.path.join(candidate_bins[0], exe_name)
    if not os.path.exists(exe_path):
        raise FileNotFoundError("termal not found at: {0}".format(exe_path))
    if not sys.platform.startswith('win') and not os.access(exe_path, os.X_OK):
        current_mode = os.stat(exe_path).st_mode
        os.chmod(exe_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return exe_path


def action(args):
    msa_path = args.msa_file
    if not os.path.exists(msa_path):
        raise argparse.ArgumentTypeError(
            "MSA file not found: {0}".format(msa_path))
    exe_path = _termal_executable()
    return subprocess.call([exe_path, msa_path])
