#!/usr/bin/env python
# -*- coding: utf-8 -*-

import untangle

from setuptools import setup
from pathlib import Path

setup(
    name="untangle",
    version=untangle.__version__,
    description="Convert XML documents into Python objects",
    long_description_content_type="text/markdown",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    author="Christian Stefanescu",
    author_email="hello@stchris.net",
    url="http://github.com/stchris//untangle",
    py_modules=["untangle"],
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

# vim: set expandtab ts=4 sw=4:
