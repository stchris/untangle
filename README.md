untangle
========

[![Build Status](https://secure.travis-ci.org/stchris/untangle.png?branch=master)](http://travis-ci.org/stchris/untangle) [![Code Quality](https://landscape.io/github/stchris/untangle/master/landscape.png)](https://landscape.io/github/stchris/untangle/master) [![Coverage Status](https://coveralls.io/repos/stchris/untangle/badge.png)](https://coveralls.io/r/stchris/untangle) [![PyPi version](https://img.shields.io/pypi/v/untangle.svg)](https://pypi.python.org/pypi/untangle)

[Documentation](http://readthedocs.org/docs/untangle/en/latest/)

* Converts XML to a Python object.
* Siblings with similar names are grouped into a list.
* Children can be accessed with ``parent.child``, attributes with ``element['attribute']``.
* You can call the ``parse()`` method with a filename, an URL or an XML string.
* Substitutes ``-``, ``.`` and ``:`` with ``_`` ``<foobar><foo-bar/></foobar>`` can be accessed with ``foobar.foo_bar``, ``<foo.bar.baz/>`` can be accessed with ``foo_bar_baz`` and ``<foo:bar><foo:baz/></foo:bar>`` can be accessed with ``foo_bar.foo_baz``
* Works with Python 2.6, 2.7 and 3.3, 3.4, 3.5, 3.6 and pypy

Installation
------------

```
pip install untangle
```

Usage
-----
(See and run <a href="https://github.com/stchris/untangle/blob/master/examples.py">examples.py</a> or this blog post: [Read XML painlessly](http://pythonadventures.wordpress.com/2011/10/30/read-xml-painlessly/) for more info)

```python
import untangle
obj = untangle.parse(resource)
```

``resource`` can be:

* a URL
* a filename
* an XML string

Running the above code and passing this XML:

```xml
<?xml version="1.0"?>
<root>
	<child name="child1"/>
</root>
```
allows it to be navigated from the ``untangle``d object like this:

```python
obj.root.child['name'] # u'child1'
```

Changelog
---------

see CHANGELOG.md
