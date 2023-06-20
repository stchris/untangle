untangle
========

[![Build Status](https://github.com/stchris/untangle/actions/workflows/build.yml/badge.svg)](https://github.com/stchris/untangle/actions)
[![PyPi version](https://img.shields.io/pypi/v/untangle.svg)](https://pypi.python.org/pypi/untangle)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

[Documentation](http://readthedocs.org/docs/untangle/en/latest/)

* Converts XML to a Python object.
* Siblings with similar names are grouped into a list.
* Children can be accessed with ``parent.child``, attributes with ``element['attribute']``.
* You can call the ``parse()`` method with a filename, an URL or an XML string.
* Substitutes ``-``, ``.`` and ``:`` with ``_`` ``<foobar><foo-bar/></foobar>`` can be accessed with ``foobar.foo_bar``, ``<foo.bar.baz/>`` can be accessed with ``foo_bar_baz`` and ``<foo:bar><foo:baz/></foo:bar>`` can be accessed with ``foo_bar.foo_baz``
* Works with Python 3.7 - 3.11

Installation
------------

With pip:
```
pip install untangle
```

With conda:
```
conda install -c conda-forge untangle
```

Conda feedstock maintained by @htenkanen. Issues and questions about conda-forge packaging / installation can be done [here](https://github.com/conda-forge/untangle-feedstock/issues).

Usage
-----
(See and run <a href="https://github.com/stchris/untangle/blob/main/examples.py">examples.py</a> or this blog post: [Read XML painlessly](http://pythonadventures.wordpress.com/2011/10/30/read-xml-painlessly/) for more info)

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
