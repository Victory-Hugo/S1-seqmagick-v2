#!/usr/bin/env python

import os
import sys

if __name__ == '__main__':
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from seqmagick2.scripts import cli
    sys.exit(cli.main(sys.argv[1:]))
