untangle
--------
.. image:: https://github.com/stchris/untangle/actions/workflows/build.yml/badge.svg

untangle parses an XML document and returns a Python object which makes it
easy to access the data you want.

Example:

::

    import untangle
    obj = untangle.parse('<root><child name="child1"/></root>')
    assert obj.root.child['name'] == u'child1'

See http://github.com/stchris/untangle and
    http://readthedocs.org/docs/untangle/en/latest/
