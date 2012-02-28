#!/usr/bin/env python

"""
 untangle

 Converts xml to python objects.

 The only method you need to call is parse()
 
 Partially inspired by xml2obj 
 (http://code.activestate.com/recipes/149368-xml2obj/)

 Author: Christian Stefanescu (http://0chris.com)
 License: MIT License - http://www.opensource.org/licenses/mit-license.php
"""

import os
from xml.sax import make_parser, handler, SAXParseException
from StringIO import StringIO

__version__ = '0.4.0'


class ParseException(Exception):
    """
    Something happened while parsing the XML data.
    """
    pass


class Element():
    """
    Representation of an XML element.
    """
    def __init__(self, name, attributes):
        self._name = name
        self._attributes = attributes
        self.children = []
        self.is_root = False
        self.cdata = ''

    def add_child(self, element):
        element._name = element._name.replace('-', '_')
        element._name = element._name.replace('.', '_')
        element._name = element._name.replace(':', '_')
        self.children.append(element)

    def add_cdata(self, cdata):
        self.cdata = self.cdata + cdata

    def get_attribute(self, key):
        return self._attributes.get(key)

    def get_elements(self, name=None):
        if name:
            return [e for e in self.children if e.name == name]
        else:
            return self.children

    def __getitem__(self, key):
        return self.get_attribute(key)

    def __getattr__(self, key):
        l = [x for x in self.children if x._name == key]
        if l:
            if len(l) == 1:
                self.__dict__[key] = l[0]
                return l[0]
            else:
                self.__dict__[key] = l
                return l
        else:
            raise IndexError('Unknown key <%s>' % key)

    def __str__(self):
        return "Element <%s> with attributes %s and children %s" % \
                (self._name, self._attributes, self.children)

    def __repr__(self):
        return "Element(name = %s, attributes = %s, cdata = %s)" % \
                (self._name, self._attributes, self.cdata)

    def __nonzero__(self):
        return self.is_root or self._name is not None

    def __eq__(self, val):
        return self.cdata == val



class Handler(handler.ContentHandler):
    """
    SAX handler which creates the Python object structure out of ``Element``s
    """
    def __init__(self):
        self.root = Element(None, None)
        self.root.is_root = True
        self.elements = []

    def startElement(self, name, attributes):
        attrs = dict()
        for k, v in attributes.items():
            attrs[k] = v
        element = Element(name, attrs)
        if len(self.elements) > 0:
            self.elements[-1].add_child(element)
        else:
            self.root.add_child(element)
        self.elements.append(element)

    def endElement(self, name):
        self.elements.pop()

    def characters(self, cdata):
        self.elements[-1].add_cdata(cdata)


def parse(filename):
    """
    Interprets the given string as a filename, URL or XML data string,
    parses it and returns a Python object which represents the given
    document.

    Raises ``ValueError`` if the argument is None / empty string.

    Raises ``untangle.ParseException`` if something goes wrong
    during parsing.
    """
    if filename is None or filename.strip() == '':
        raise ValueError('parse() takes a filename, URL or XML string')
    parser = make_parser()
    handler = Handler()
    parser.setContentHandler(handler)
    try:
        if os.path.exists(filename) or is_url(filename):
            parser.parse(filename)
        else:
            parser.parse(StringIO(filename))
    except SAXParseException, e:
        raise ParseException(e)

    return handler.root

def is_url(s):
    return s.startswith('http://') or s.startswith('https://')

# vim: set expandtab ts=4 sw=4:
