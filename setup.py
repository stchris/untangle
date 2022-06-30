#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
untangle
--------
.. image:: https://secure.travis-ci.org/stchris/untangle.png?branch=main

untangle parses an XML document and returns a Python object which makes it
easy to access the data you want.

Example:

::

    import untangle
    obj = untangle.parse('<root><child name="child1"/></root>')
    assert obj.root.child['name'] == u'child1'

See http://github.com/stchris/untangle and
    http://readthedocs.org/docs/untangle/en/latest/
"""

import untangle

from setuptools import setup

setup(
    name="untangle",
    version=untangle.__version__,
    description="Convert XML documents into Python objects",
    long_description=__doc__,
    author="Christian Stefanescu",
    author_email="hello@stchris.net",
    url="http://github.com/stchris//untangle",
    py_modules=["untangle"],
    license="MIT",
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ),
)

# vim: set expandtab ts=4 sw=4:
