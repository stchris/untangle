untangle 
========
version 0.1
by Christian Stefanescu (http://0chris.com)

What it does
============
* Converts XML to a Python object. 
* Siblings with similar names are grouped into a list. 
* Children can be accessed with ``parent.child``, attributes with ``element['attribute']``.
* You can call the ``parse()`` method with a filename, an URL or an XML string.
* Substitutes ``-`` with ``_`` so ``<foobar><foo-bar/></foobar>`` can be accessed with ``foobar.foo_bar``

Usage
=====

```python
import untangled
obj = untangled.parse(resource)
```

``resource`` can be:

* an URL
* a filename
* an XML string

This XML:

```xml
<?xml version="1.0"?>
<root>
	<child name="child1">
</root>
```
allows you to access the following:

```python
obj.root.child['name'] # u'child1'
```

Also: see examples.py

