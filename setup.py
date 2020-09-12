#!/usr/bin/env python

"""
Setup script for ais_tools
"""

from setuptools import find_packages
from setuptools import setup

import codecs

package = __import__('ais_tools')


DEPENDENCIES = [
    "libais",
    "Click==7.0",
    "gpxpy",
    "requests",
    "bitstring",
    "Flask-API",
]

DEV_DEPENDENCIES = [
    'pytest',
    'pytest-cov',
    'flake8'
]

with codecs.open('README.md', encoding='utf-8') as f:
    readme = f.read().strip()

with codecs.open('requirements.txt', encoding='utf-8') as f:
    DEPENDENCY_LINKS = [line for line in f]

setup(
    author=package.__author__,
    author_email=package.__email__,
    description=package.__doc__.strip(),
    extras_require={'dev': DEV_DEPENDENCIES},
    include_package_data=True,
    install_requires=DEPENDENCIES,
    license="Apache 2.0",
    long_description=readme,
    name='ais-tools',
    packages=find_packages(exclude=['test*.*', 'tests']),
    url=package.__source__,
    version=package.__version__,
    zip_safe=True,
    dependency_links=DEPENDENCY_LINKS,
    entry_points='''
        [console_scripts]
        ais_tools=ais_tools.cli:cli
    ''',
)
