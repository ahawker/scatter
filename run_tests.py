#!/usr/bin/env python
"""
    run_tests.py
    ~~~~~~~~~~~~

    Entry point for running Scatter test suite.
"""

import os
import sys


if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    from scatter.tests import main
    main()
