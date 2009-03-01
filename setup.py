# -*- coding: utf-8 -*-

from setuptools import setup

import exetractor


setup(
    name='exetractor',
    author='Andreas Stuehrk',
    license=exetractor.__license__,
    version=exetractor.__version__,
    packages=['exetractor'],
    entry_points={
        'console_scripts': [
            'exetract = exetractor:main'
        ]
    },
    install_requires=['pefile>=1.2.8']
)
