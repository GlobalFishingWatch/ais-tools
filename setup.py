"""
Minimal setup.py for C extension compilation.

All other package config is in pyproject.toml.
"""

import sys
from setuptools import Extension, setup

extra_compile_args = []
if sys.platform != "win32":
    extra_compile_args = ["-std=c11", "-Wall", "-Werror", "-O3"]

source_path = "ais_tools/core/"
sources = [
    f"{source_path}checksum.c",
    f"{source_path}methods.c",
    f"{source_path}module.c",
    f"{source_path}strcpy.c",
]

setup(
    ext_modules=[
        Extension(
            "ais_tools.core",
            sources=sources,
            include_dirs=[source_path],
            extra_compile_args=extra_compile_args,
        )
    ],
)
