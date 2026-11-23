.. untangle documentation master file, created by
   sphinx-quickstart on Fri Apr  6 16:05:20 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

untangle: Convert XML to Python objects
=======================================

`untangle <https://github.com/stchris/untangle/>`_ is a tiny Python library which converts an XML
document to a Python object. It is available under the `MIT license <https://github.com/stchris/untangle/blob/main/LICENSE/>`_.

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

Use an explicit entry point when the kind of input is known. These functions
do not guess whether the input is a local path, XML text or a URL. Existing
``parse()`` calls remain supported, including file-like objects.

.. autofunction:: parse_file

.. autofunction:: parse_xml_string

.. autofunction:: parse_url

For example::

    >>> import untangle
    >>> doc = untangle.parse_xml_string('<root><child name="example"/></root>')
    >>> doc.root.child['name']
    'example'

If you are looking for information on a specific function, class or method, this part of the documentation is for you.

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

For text/data inbetween tags, this is described as cdata. After specifying the relevant element as explained above, the data/cdata can be accessed by adding ".cdata" (without the quotes) to the end of your dictionary call.

For more examples, have a look at (and launch) `examples.py <https://github.com/stchris/untangle/blob/main/examples.py/>`_.

Installation
------------

::

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

Some names, such as ``children``, ``cdata`` and ``is_root``, are already used
by ``Element``. For an XML child with one of these names, use
``parent.get_elements(name)``. This method always returns a list of matching
direct children, even when there is only one match::

    >>> import untangle
    >>> doc = untangle.parse(
    ...     '<root><children>first</children><other/><children>second</children></root>'
    ... )
    >>> [child.cdata for child in doc.root.get_elements('children')]
    ['first', 'second']
    >>> len(doc.root.children)  # The complete list of direct children
    3
    >>> doc.root.get_elements('missing')
    []

Pass the normalized name to ``get_elements``, for example ``foo_bar`` for
``<foo-bar/>``. Square brackets, such as ``element['name']``, retrieve XML
attributes rather than child elements.

Encoding
---------

Be aware that with certain characters or maybe also depending on the python version you might get an error on accessing specific attributes, such as ``UnicodeEncodeError: 'ascii' codec can't encode character u'\xfc' in position 385: ordinal not in range(128)``
In most cases it should be enough to import the sys module, and set utf-8 as encoding, with: ::

   import sys
   reload(sys) # just to be sure
   sys.setdefaultencoding('utf-8')

SAX features
------------

It is possible to pass specific SAX features to the handler used by untangle, for instance: ::

    untangle.parse(my_xml, feature_external_ges=False)

This will toggle the SAX handler feature described `here <https://docs.python.org/2/library/xml.sax.handler.html#xml.sax.handler.feature_external_ges>`_.

Changelog
---------

see https://github.com/stchris/untangle/blob/main/CHANGELOG.md


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
