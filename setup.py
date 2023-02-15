#!/usr/bin/env python

"""
Setup script for ais_tools
"""

from setuptools import find_packages
from setuptools import setup

import codecs

import sys
from setuptools import Extension

package = __import__('ais_tools')

extra_compile_args = []
extra_link_args = []
undef_macros = []


if sys.platform == "win32":
    extra_compile_args += []
else:
    extra_compile_args += ["-std=c11", "-Wall", "-Werror", "-O3"]


DEPENDENCIES = [
    "libais",
    "Click",
    "gpxpy",
    "requests",
    "bitarray",
    "cbitstruct",
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
        ais-tools=ais_tools.cli:cli
    ''',
    ext_modules=[
        Extension(
            "ais_tools.core",
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            sources=["ais_tools/core/module.c",
                     "ais_tools/core/methods.c",
                     "ais_tools/core/join_tagblock.c",
                     "ais_tools/core/split_tagblock.c",
                     "ais_tools/core/tagblock_fields.c",
                     "ais_tools/core/tagblock_decode.c",
                     "ais_tools/core/tagblock_encode.c",
                     "ais_tools/core/checksum.c",
                     "ais_tools/core/strcpy.c",
                     ],
            include_dirs=["ais_tools/"],
            undef_macros=undef_macros,
        ),
        Extension(
            "ais_tools._tagblock",
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            sources=["ais_tools/core/tagblock.c",
                     "ais_tools/core/tagblock_fields.c",
                     "ais_tools/core/tagblock_decode.c",
                     "ais_tools/core/tagblock_encode.c",
                     "ais_tools/core/methods.c",
                     "ais_tools/core/checksum.c",
                     "ais_tools/core/strcpy.c"],
            include_dirs=["ais_tools/"],
            undef_macros=undef_macros,
        )
    ],
)
