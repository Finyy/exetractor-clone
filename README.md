exetractor-clone
================

A far from complete unpacker for packed Python executables.

```
$ python2 exetractor.py
Usage: exetractor.py <path to exe>
```

For PyInstaller generated apps, use ArchiveExtractor.py utility.

* Extract pyc (and py) files using ArchiveExtractor.py utility,

```

$ python2 utils/ArchiveExtractor.py ~/testapp
...
Extracting bytecode to output/mylib.pyc
Extracting source to output/hello.py

File(s) were extracted to output directory.
```

* Use uncompyle2 to decompile pyc files,

```

$  python2 ~/uncompyle2/uncompyle2.py  output/mylib.pyc 
..
print 'mylib'
# okay decompyling output/mylib.pyc 
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed


```
