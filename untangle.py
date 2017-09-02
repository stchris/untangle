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
import sys
import keyword
import errno
from xml.sax import make_parser, handler
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    from types import StringTypes

    def is_string(x):
        return isinstance(x, StringTypes)
except ImportError:
    def is_string(x):
        return isinstance(x, str)

__version__ = '1.1.1'


class Element(object):
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
        """
        Store child elements.
        """
        self.children.append(element)

    def add_cdata(self, cdata):
        """
        Store cdata
        """
        self.cdata = self.cdata + cdata

    def get_attribute(self, key):
        """
        Get attributes by key
        """
        return self._attributes.get(key)

    def get_elements(self, name=None):
        """
        Find a child element by name
        """
        if name:
            return [e for e in self.children if e._name == name]
        else:
            return self.children

    def __getitem__(self, key):
        return self.get_attribute(key)

    def __getattr__(self, key):
        matching_children = [x for x in self.children if x._name == key]
        if matching_children:
            if len(matching_children) == 1:
                self.__dict__[key] = matching_children[0]
                return matching_children[0]
            else:
                self.__dict__[key] = matching_children
                return matching_children
        else:
            raise AttributeError(
                "'%s' has no attribute '%s'" % (self._name, key)
            )

    def __hasattribute__(self, name):
        if name in self.__dict__:
            return True
        return any(self.children, lambda x: x._name == name)

    def __iter__(self):
        yield self

    def __str__(self):
        return (
            "Element <%s> with attributes %s, children %s and cdata %s" %
            (self._name, self._attributes, self.children, self.cdata)
        )

    def __repr__(self):
        return (
            "Element(name = %s, attributes = %s, cdata = %s)" %
            (self._name, self._attributes, self.cdata)
        )

    def __nonzero__(self):
        return self.is_root or self._name is not None

    def __eq__(self, val):
        return self.cdata == val

    def __dir__(self):
        children_names = [x._name for x in self.children]
        return children_names

    def __len__(self):
        return len(self.children)

    def __contains__(self, key):
        return key in dir(self)


class Handler(handler.ContentHandler):
    """
    SAX handler which creates the Python object structure out of ``Element``s
    """
    def __init__(self):
        self.root = Element(None, None)
        self.root.is_root = True
        self.elements = []

    def startElement(self, name, attributes):
        name = name.replace('-', '_')
        name = name.replace('.', '_')
        name = name.replace(':', '_')

        # adding trailing _ for keywords
        if keyword.iskeyword(name):
            name += '_'

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


def parse(filename, **parser_features):
    """
    Interprets the given string as a filename, URL or XML data string,
    parses it and returns a Python object which represents the given
    document.

    Extra arguments to this function are treated as feature values to pass
    to ``parser.setFeature()``. For example, ``feature_external_ges=False``
    will set ``xml.sax.handler.feature_external_ges`` to False, disabling
    the parser's inclusion of external general (text) entities such as DTDs.

    Raises ``ValueError`` if the first argument is None / empty string.

    Raises ``AttributeError`` if a requested xml.sax feature is not found in
    ``xml.sax.handler``.

    Raises ``xml.sax.SAXParseException`` if something goes wrong
    during parsing.
    """
    if (filename is None or (is_string(filename) and filename.strip()) == ''):
        raise ValueError('parse() takes a filename, URL or XML string')
    parser = make_parser()
    for feature, value in parser_features.items():
        parser.setFeature(getattr(handler, feature), value)
    sax_handler = Handler()
    parser.setContentHandler(sax_handler)
    if (is_pathname_valid(filename) and os.path.exists(filename)) or (is_string(filename) and is_url(filename)):
        parser.parse(filename)
    else:
        if hasattr(filename, 'read'):
            parser.parse(filename)
        else:
            parser.parse(StringIO(filename))

    return sax_handler.root

# Originally based on https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta/34102855#34102855
def is_pathname_valid(pathname):
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.

    # Sadly, Python fails to provide the following magic number for us.
    ERROR_INVALID_NAME = 123
    '''
    Windows-specific error code indicating an invalid pathname.
    
    See Also
    ----------
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms681382%28v=vs.85%29.aspx
        Official listing of all such codes.
    '''

    try:
        if not is_string(pathname) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
            except ValueError:
                # Python throws its own exceptions if a path isn't valid in some cases, e.g. e.g. 'path too long for Windows':
                # https://github.com/python/cpython/blob/3.6/Modules/posixmodule.c#L929
                return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
        # If any other exception was raised, this is an unrelated fatal issue
        # (e.g., a bug). Permit this exception to unwind the call stack.
        #
        # Did we mention this should be shipped with Python already?


def is_url(string):
    """
    Checks if the given string starts with 'http(s)'.
    """
    try:
        return string.startswith('http://') or string.startswith('https://')
    except AttributeError:
        return False

# vim: set expandtab ts=4 sw=4:
