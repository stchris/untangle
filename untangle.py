#!/usr/bin/env python

"""
 untangle 

 Converts xml to python objects.

 Author: Christian Stefanescu (http://0chris.com)
"""

from xml.sax import make_parser, handler
from StringIO import StringIO

class Element():
	def __init__(self, name, attributes):
		self.name = name
		self.attributes = attributes
		self.children = []

	def add_child(self, element):
		element.name = element.name.replace('-', '_')
		self.children.append(element)

	def get_attribute(self, key):
		return self.attributes.get(key)

	def get_elements(self, name=None):
		if name:
			return [e for e in self.children if e.name == name]
		else:
			return self.children

	def __getitem__(self, key):
		return self.get_attribute(key)

	def __getattr__(self, key):
		l = [x for x in self.children if x.name == key]
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
		return "Element <%s> with attributes %s and children %s" % (self.name, self.attributes, self.children)

	def __repr__(self):
		return "Element(name = %s, attributes = %s)" % (self.name, self.attributes)

	def __nonzero__(self):
		return self.name is not None

class Handler(handler.ContentHandler):
	def __init__(self):
		self.root = Element(None, None)
		self.elements = []

	def startElement(self, name, attributes):
		attrs = dict()
		for k,v in attributes.items():
			attrs[k] = v
		element = Element(name, attrs)
		if len(self.elements) > 0:
			self.elements[-1].add_child(element)
		else:
			self.root.add_child(element)
		self.elements.append(element)

	def endElement(self, name):
		self.elements.pop()

def parse(filename):
	parser = make_parser()
	handler = Handler()
	parser.setContentHandler(handler)
	try:
		parser.parse(filename)
	except IOError as e:
		# try to see if the passed string is valid XML before giving up
		parser.parse(StringIO(filename))

	return handler.root

