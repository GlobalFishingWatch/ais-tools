#!/usr/bin/env python

"""
Setup script for ais_tools
"""

from setuptools import find_packages
from setuptools import setup

import codecs

import sys
import os
from setuptools import Extension

# package = __import__('ais_tools')

extra_compile_args = []
extra_link_args = []
undef_macros = []


if sys.platform == "win32":
    extra_compile_args += []
else:
    extra_compile_args += ["-std=c11", "-Wall", "-Werror", "-O3"]

source_path = 'ais_tools/core/'
sources = [f'{source_path}{file}' for file in os.listdir(source_path) if file.endswith('.c')]
core_module = Extension(
    "ais_tools.core",
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    sources=sources,
    include_dirs=[source_path],
    undef_macros=undef_macros,
)


with codecs.open('requirements.txt', encoding='utf-8') as f:
    DEPENDENCY_LINKS = [line for line in f]

setup(
    include_package_data=True,
    packages=find_packages(exclude=['test*.*', 'tests']),
    zip_safe=True,
    dependency_links=DEPENDENCY_LINKS,
    ext_modules=[core_module],
)
