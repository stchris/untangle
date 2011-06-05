untangle 
========

* Converts XML to a Python object. 
* Siblings with similar names are grouped into a list. 
* Children can be accessed with ``parent.child``, attributes with ``element['attribute']``.
* You can call the ``parse()`` method with a filename, an URL or an XML string.
* Substitutes ``-`` with ``_`` so ``<foobar><foo-bar/></foobar>`` can be accessed with ``foobar.foo_bar``

Installation
------------

```
git clone git://github.com/stchris/untangle.git
python setup.py test
python setup.py install
```

Works on Python 2.6, 2.7 and Pypy so far.

Usage
-----
(See and run <a href="https://github.com/stchris/untangle/blob/master/examples.py">examples.py</a> for more info)

```python
import untangle
obj = untangle.parse(resource)
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
can be navigated from the ``untangle``d object like this:

```python
obj.root.child['name'] # u'child1'
```

