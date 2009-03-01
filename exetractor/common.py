# -*- coding: utf-8 -*-


"""
    exetractor.common
    ~~~~~~~~~~~~~~~~~

    :copyright: (c) 2009 by Andreas Stührk
    :license: modified BSD, see LICENSE for more details.
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
