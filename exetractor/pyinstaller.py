# -*- coding: utf-8 -*-


"""
    exetractor.pyinstaller
    ~~~~~~~~~~~~~~~~~~~~~~

    Extractor for executable files created with PyInstaller.

    :copyright: (c) 2009 by Andreas Stührk
    :license: modified BSD, see LICENSE for more details.
"""


from __future__ import with_statement

import marshal
import struct
import sys
from dis import disassemble
from zlib import decompress

from .common import wrap_stdio


class Cookie(object):
    # COOKIE magic (see source/common/launch.h)
    MAGIC = 'MEI\014\013\012\013\016'
   
    def __init__(self, data):
        assert data.startswith(Cookie.MAGIC)
        data = data[len(Cookie.MAGIC):]
        (self.len,
         self.toc,
         self.toclen,
         self.pyver) = struct.unpack('!4i', data)

    size = struct.calcsize('!4i') + len(MAGIC)


class TOCEntry(object):
    def __init__(self, data):
        (self.structlen,
         self.pos,
         self.len,
         self.ulen,
         self.cflag,
         self.typcd,
         self.name) = struct.unpack('!4i3c', data[:TOCEntry.size])
        # Get complete name
        self.name += data[TOCEntry.size:data.index('\x00', TOCEntry.size)]
        # Convert cflag to Boolean
        self.cflag = self.cflag == '\x01'

    size = struct.calcsize('!4i3c')


class TOC(object):
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        i = 0
        while i < len(self.data):
            entry = TOCEntry(self.data[i:])
            yield entry
            i += entry.structlen


def is_valid_data(exe_data):
    try:
        cookie = Cookie(exe_data[-Cookie.size:])
        assert cookie.len > 0 and cookie.toc > 0 and cookie.toclen > 0
    except AssertionError:
        return False
    return True


def unpack(exe_data):
    cookie = Cookie(exe_data[-Cookie.size:])
    same_pyver = cookie.pyver == sys.version_info[0] * 10 + sys.version_info[1]
    if not same_pyver:
        print ('Warning: Python version does not match, '
               'will not unmarshal data')
    pkgstart = -cookie.len
    tocdata = exe_data[pkgstart + cookie.toc:
                       pkgstart + cookie.toc + cookie.toclen]
    # Extract strings
    for entry in TOC(tocdata):
        data = exe_data[pkgstart + entry.pos:
                        pkgstart + entry.pos + entry.len]
        if entry.cflag:
            data = decompress(data)
        if entry.typcd.lower() == 'm':
            # Module
            print 'Extracting module', entry.name
            with open(entry.name + '.pyc', 'wb') as outfile:
                outfile.write(data)
            if same_pyver:
                print 'Disassembling module', entry.name
                # skip header of pyc/pyo files and unmarshal the code
                # object
                code_object = marshal.loads(data[8:])
                # Write dis output to file
                # Note: this is a hack, but dis seems to be a hack, too
                with wrap_stdio(open(entry.name + '.dis', 'w')):
                    disassemble(code_object)
        elif entry.typcd == 's':
            print 'Extracting script', entry.name
            # Python script
            with open(entry.name + '.py', 'w') as outfile:
                outfile.write(data)
