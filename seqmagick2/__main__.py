#!/usr/bin/env python
"""
Entry point for seqmagick2 when run as a module with python -m seqmagick2
"""

from seqmagick2.scripts.cli import main
import sys

if __name__ == '__main__':
    sys.exit(main())