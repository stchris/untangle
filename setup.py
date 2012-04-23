#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
untangle
--------
.. image:: https://secure.travis-ci.org/stchris/untangle.png?branch=master

untangle parses an XML document and returns a Python object which makes it
easy to access the data you want.

Example:

::

    import untangle
    obj = untangle.parse('<root><child name="child1"/></root>')
    assert obj.root.child['name'] == u'child1'

See http://stchris.github.com/untangle and http://readthedocs.org/docs/untangle/en/latest/
"""

import os
import sys
import untangle

from setuptools import setup

if sys.argv[-1] == 'test':
    os.system('nosetests tests/tests.py')
    sys.exit()

setup(
    name='untangle',
    version=untangle.__version__,
    description='Convert XML documents into Python objects',
    long_description=__doc__,
    author='Christian Stefanescu',
    author_email='st.chris@gmail.com',
    url='http://stchris.github.com/untangle',
    py_modules=['untangle'],
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
    ),
    test_suite = 'nose.collector'
)

# vim: set expandtab ts=4 sw=4:
