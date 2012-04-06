.. untangle documentation master file, created by
   sphinx-quickstart on Fri Apr  6 16:05:20 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

untangle: Convert XML to Python objects
=======================================

`untangle <https://stchris.github.com/untangle/>`_ is a tiny Python library which converts an XML
document to a Python object. It is available under the `MIT license <https://github.com/stchris/untangle/blob/master/LICENSE/>`_.

.. contents::

Usage
-----
.. module:: untangle

untangle has a very simple API. You just need to call the
parse function to get back a Python object. The parameter
can be:

* a string
* a filename
* a URL

.. autofunction:: parse
If you are looking for information on a specific function, class or method,
this part of the documentation is for you.

The object you get back represents the complete XML document. Child elements can be accessed with ``parent.child``, attributes with ``element['attribute']``. Siblings with similar names are grouped into a list.

Example
-------

Considering this XML document: ::

    <?xml version="1.0"?>
    <root>
        <child name="child1"/>
    </root>

and assuming it's available in a variable called `xml`, we could use untangle like this: ::

    doc = untangle.parse(xml)
    child_name = doc.root.child['name'] # 'child1'

For more examples, have a look at (and launch) `examples.py <https://github.com/stchris/untangle/blob/master/examples.py/>`_.

Installation
------------

It is recommended to use pip, which will always download the latest stable release: ::

    pip install untangle

Motivation
----------

untangle is available for that use case, where you have a 20-line XML file you got back from an API and you just need to extract some values out of it. You might not want to use regular expressions, but just as well you might not want to install a complex libxml2-based solution (and look up its terse API).

Performance and memory usage might be bad, but these tradeoffs were made in order to allow a simple API and no external dependencies. See also: Limitations_.


Limitations
-----------

untangle trades features for a simple API, which is why untangle substitutes ``-``, ``.`` and ``:`` with ``_``:

* ``<foobar><foo-bar/></foobar>`` can be accessed with ``foobar.foo_bar``
* ``<foo.bar.baz/>`` can be accessed with ``foo_bar_baz``
* ``<foo:bar><foo:baz/></foo:bar>`` can be accessed with ``foo_bar.foo_baz``


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

