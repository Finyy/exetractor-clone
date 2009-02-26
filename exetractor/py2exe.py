# -*- coding: utf-8 -*-


"""
    exetractor.py2exe
    ~~~~~~~~~~~~~~~~~

    Extractor for exe files created with py2exe.
"""

from __future__ import with_statement

import marshal
import struct
from dis import disassemble
from os.path import basename

from pefile import PE

from .common import wrap_stdio


class ScriptInfo(object):
    def __init__(self, data):
        (self.tag,
         self.optimize,
         self.unbuffered,
         self.data_bytes) = struct.unpack('4i', data[:ScriptInfo.size])

    size = struct.calcsize('4i')


def locate_script(exe):
    # Get PYTHONSCRIPT resource
    entry = get_resource(exe, 'PYTHONSCRIPT').directory.entries[0]
    # Get the RVA of the resource and its size
    data_rva = entry.directory.entries[0].data.struct.OffsetToData
    size = entry.directory.entries[0].data.struct.Size
    # Get the data of the resource
    data = exe.get_memory_mapped_image()[data_rva:data_rva + size]
    # Validate script resource
    scriptinfo = ScriptInfo(data)
    # tag magic (see source/start.c)
    assert scriptinfo.tag == 0x78563412
    data = data[ScriptInfo.size:]
    return (scriptinfo, data)


def get_resource(exe, name):
    for entry in exe.DIRECTORY_ENTRY_RESOURCE.entries:
        if entry.name and entry.name.string == name:
            return entry
    else:
        raise ValueError('resource `' + name + '` not found')


def is_valid_data(data):
    """
    Small function to determine whether `data` seems to be a valid target
    or not.
    """
    if not data.startswith('MZ'):
        return False
    # Seems to be a PE file
    exe = PE(data=data)
    # Try to load the PYTHONSCRIPT resource
    try:
        locate_script(exe)
    except (AssertionError, ValueError):
        return False
    return True


def unpack(exe_data):
    exe = PE(data=exe_data)
    scriptinfo, data = locate_script(exe)
    # Get library path
    libfilename = data[:data.index('\x00')]
    data = data[len(libfilename) + 1:]
    # Load `marshal`ed list of code objects
    # Note: This will likely fail if the exe was built with a different
    #       python version
    print 'Extracting marshalled code objects'
    with open('code_objects.marshal', 'wb') as outfile:
        outfile.write(data)
    for code_object in marshal.loads(data):
        print 'Disassembling', code_object.co_filename
        with wrap_stdio(open(basename(code_object.co_filename) + '.dis',
                                      'w')):
            disassemble(code_object)
    # Extract library archive if required
    if not libfilename:
        print 'Extracting library.zip'
        with open('library.zip', 'wb') as outfile:
            # PK\x03\x04 == zip file magic
            outfile.write(exe_data[exe_data.index('PK\x03\x04'):])
