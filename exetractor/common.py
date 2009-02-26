# -*- coding: utf-8 -*-


"""
    exetractor.common
    ~~~~~~~~~~~~~~~~~
"""

import sys
from contextlib import contextmanager


@contextmanager
def wrap_stdio(new_stdio, close=True):
    try:
        sys.stdout, orig_stdout = new_stdio, sys.stdout
        yield new_stdio
    finally:
        sys.stdout = orig_stdout
        if close:
            new_stdio.close()
