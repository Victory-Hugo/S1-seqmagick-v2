#!/usr/bin/env python

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages

subprocess.call(
    ('mkdir -p seqmagick2/data && '
     'git describe --tags --dirty > seqmagick2/data/ver.tmp '
     '&& mv seqmagick2/data/ver.tmp seqmagick2/data/ver '
     '|| rm -f seqmagick2/data/ver.tmp'),
    shell=True, stderr=open(os.devnull, "w"))

def _read_version():
    version_file = Path(__file__).parent / 'seqmagick2' / 'data' / 'ver'
    if version_file.exists():
        return version_file.read_text(encoding='utf-8').strip()
    return '1.0.0'

__version__ = _read_version()

setup(name='seqmagick2',
      version=__version__,
      description='Tools for converting and modifying sequence files '
      'from the command-line',
      url='http://github.com/fhcrc/seqmagick2',
      download_url='http://pypi.python.org/pypi/seqmagick2',
      author='Matsen Group',
      # author_email='http://matsen.fhcrc.org/',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'seqmagick2 = seqmagick2.scripts.cli:main'
          ]},
      package_data={
          'seqmagick2': ['data/*'],
          'seqmagick2.test.integration': ['data/*']
      },
      python_requires='>=3.9',
      install_requires=['biopython>=1.78', 'pygtrie>=2.1'],
      classifiers=[
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
      ],
      license="GPL V3")
