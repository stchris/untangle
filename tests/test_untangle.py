#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import untangle
import xml


class FromStringTestCase(unittest.TestCase):
    """ Basic parsing tests with input as string """
    def test_basic(self):
        o = untangle.parse("<a><b/><c/></a>")
        self.assert_(o is not None)
        self.assert_(o.a is not None)
        self.assert_(o.a.b is not None)
        self.assert_(o.a.c is not None)
        self.assert_('a' in o)
        self.assert_('b' in o.a)
        self.assert_('c' in o.a)
        self.assert_('d' not in o.a)

    def test_basic_with_decl(self):
        o = untangle.parse("<?xml version='1.0'?><a><b/><c/></a>")
        self.assert_(o is not None)
        self.assert_(o.a is not None)
        self.assert_(o.a.b is not None)
        self.assert_(o.a.c is not None)
        self.assert_('a' in o)
        self.assert_('b' in o.a)
        self.assert_('c' in o.a)
        self.assert_('d' not in o.a)

    def test_with_attributes(self):
        o = untangle.parse('''
                    <Soup name="Tomato soup" version="1">
                     <Ingredients>
                        <Water qty="1l" />
                        <Tomatoes qty="1kg" />
                        <Salt qty="1tsp" />
                     </Ingredients>
                     <Instructions>
                        <boil-water/>
                        <add-ingredients/>
                        <done/>
                     </Instructions>
                    </Soup>
                     ''')
        self.assertEquals('Tomato soup', o.Soup['name'])
        self.assertEquals(1, int(o.Soup['version']))
        self.assertEquals('1l', o.Soup.Ingredients.Water['qty'])
        self.assert_(o.Soup.Instructions.add_ingredients is not None)

    def test_grouping(self):
        o = untangle.parse('''
                    <root>
                     <child name="child1">
                        <subchild name="sub1"/>
                     </child>
                     <child name="child2"/>
                     <child name="child3">
                        <subchild name="sub2"/>
                        <subchild name="sub3"/>
                     </child>
                    </root>
                     ''')
        self.assert_(o.root)

        children = o.root.child
        self.assertEquals(3, len(children))
        self.assertEquals('child1', children[0]['name'])
        self.assertEquals('sub1', children[0].subchild['name'])
        self.assertEquals(2, len(children[2].subchild))
        self.assertEquals('sub2', children[2].subchild[0]['name'])

    def test_single_root(self):
        self.assert_(untangle.parse('<single_root_node/>'))

    def test_attribute_protocol(self):
        o = untangle.parse('''
                    <root>
                     <child name="child1">
                        <subchild name="sub1"/>
                     </child>
                     <child name="child2"/>
                     <child name="child3">
                        <subchild name="sub2"/>
                        <subchild name="sub3"/>
                     </child>
                    </root>
                     ''')
        try:
            self.assertEquals(None, o.root.child.inexistent)
            self.fail('Was able to access inexistent child as None')
        except AttributeError:
            pass  # this is the expected error
        except IndexError:
            self.fail('Caught IndexError quen expecting AttributeError')

        self.assertTrue(hasattr(o.root, 'child'))
        self.assertFalse(hasattr(o.root, 'inexistent'))

        self.assertEqual('child1', getattr(o.root, 'child')[0]['name'])

    def test_python_keyword(self):
        o = untangle.parse("<class><return/><pass/><None/></class>")
        self.assert_(o is not None)
        self.assert_(o.class_ is not None)
        self.assert_(o.class_.return_ is not None)
        self.assert_(o.class_.pass_ is not None)
        self.assert_(o.class_.None_ is not None)


class InvalidTestCase(unittest.TestCase):
    """ Test corner cases """
    def test_invalid_xml(self):
        self.assertRaises(
            xml.sax.SAXParseException,
            untangle.parse,
            '<unclosed>'
        )

    def test_empty_xml(self):
        self.assertRaises(ValueError, untangle.parse, '')

    def test_none_xml(self):
        self.assertRaises(ValueError, untangle.parse, None)


class PomXmlTestCase(unittest.TestCase):
    """ Tests parsing a Maven pom.xml """
    def setUp(self):
        self.o = untangle.parse('tests/res/pom.xml')

    def test_parent(self):
        project = self.o.project
        self.assert_(project)

        parent = project.parent
        self.assert_(parent)
        self.assertEquals(
            'com.atlassian.confluence.plugin.base',
            parent.groupId
        )
        self.assertEquals('confluence-plugin-base', parent.artifactId)
        self.assertEquals('17', parent.version)

        self.assertEquals('4.0.0', project.modelVersion)
        self.assertEquals('com.this.that.groupId', project.groupId)

        self.assertEquals('', project.name)
        self.assertEquals(
            '${pom.groupId}.${pom.artifactId}',
            project.properties.atlassian_plugin_key
        )
        self.assertEquals(
            '1.4.1',
            project.properties.atlassian_product_test_lib_version
        )
        self.assertEquals(
            '2.9',
            project.properties.atlassian_product_data_version
        )

    def test_lengths(self):
        self.assertEquals(1, len(self.o))
        self.assertEquals(8, len(self.o.project))
        self.assertEquals(3, len(self.o.project.parent))
        self.assertEquals(4, len(self.o.project.properties))


class NamespaceTestCase(unittest.TestCase):
    """ Tests for XMLs with namespaces """
    def setUp(self):
        self.o = untangle.parse('tests/res/some.xslt')

    def test_namespace(self):
        self.assert_(self.o)

        stylesheet = self.o.xsl_stylesheet
        self.assert_(stylesheet)
        self.assertEquals('1.0', stylesheet['version'])

        template = stylesheet.xsl_template[0]
        self.assert_(template)
        self.assertEquals('math', template['match'])
        self.assertEquals('compact', template.table['class'])
        self.assertEquals(
            'compact vam',
            template.table.tr.xsl_for_each.td['class']
        )
        self.assertEquals(
            untangle.Element('', ''),
            template.table.tr.xsl_for_each.td.xsl_apply_templates
        )

        last_template = stylesheet.xsl_template[-1]
        self.assert_(last_template)
        self.assertEquals('m_var', last_template['match'])
        self.assertEquals(
            'compact tac formula italic',
            last_template.p['class']
        )
        self.assertEquals(
            untangle.Element('xsl_apply_templates', ''),
            last_template.p.xsl_apply_templates
        )


class IterationTestCase(unittest.TestCase):
    """ Tests various cases of iteration over child nodes. """
    def test_multiple_children(self):
        """ Regular case of iteration. """
        o = untangle.parse("<a><b/><b/></a>")
        cnt = 0
        for i in o.a.b:
            cnt += 1
        self.assertEquals(2, cnt)

    def test_single_child(self):
        """ Special case when there is only a single child element.
            Does not work without an __iter__ implemented.
        """
        o = untangle.parse("<a><b/></a>")
        cnt = 0
        for i in o.a.b:
            cnt += 1
        self.assertEquals(1, cnt)


class TwimlTestCase(unittest.TestCase):
    """ Github Issue #5: can't dir the parsed object """
    def test_twiml_dir(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather action="http://example.com/calls/1/twiml?event=start"
  numDigits="1" timeout="0">
    <Play>http://example.com/barcall_message_url.wav</Play>
  </Gather>
  <Redirect>http://example.com/calls/1/twiml?event=start</Redirect>
</Response>
        """
        o = untangle.parse(xml)
        self.assertEquals([u'Response'], dir(o))
        resp = o.Response
        self.assertEquals([u'Gather', u'Redirect'], dir(resp))
        gather = resp.Gather
        redir = resp.Redirect
        self.assertEquals([u'Play'], dir(gather))
        self.assertEquals([], dir(redir))
        self.assertEquals(
            u'http://example.com/calls/1/twiml?event=start',
            o.Response.Redirect.cdata
        )


class UnicodeTestCase(unittest.TestCase):
    """ Github issue #8: UnicodeEncodeError """
    def test_unicode_file(self):
        o = untangle.parse('tests/res/unicode.xml')
        self.assertEquals(u'ðÒÉ×ÅÔ ÍÉÒ', o.page.menu.name)

    def test_lengths(self):
        o = untangle.parse('tests/res/unicode.xml')
        self.assertEquals(1, len(o))
        self.assertEquals(1, len(o.page))
        self.assertEquals(2, len(o.page.menu))
        self.assertEquals(2, len(o.page.menu.items))
        self.assertEquals(2, len(o.page.menu.items.item))
        self.assertEquals(0, len(o.page.menu.items.item[0].name))
        self.assertEquals(0, len(o.page.menu.items.item[1].name))

    def test_unicode_string(self):
        o = untangle.parse('<Element>valüé ◔‿◔</Element>')
        self.assertEquals(u'valüé ◔‿◔', o.Element.cdata)


class FileObjects(unittest.TestCase):
    """ Test reading from file-like objects """
    def test_file_object(self):
        with open('tests/res/pom.xml') as pom_file:
            o = untangle.parse(pom_file)
            project = o.project
            self.assert_(project)

            parent = project.parent
            self.assert_(parent)
            self.assertEquals(
                'com.atlassian.confluence.plugin.base',
                parent.groupId
            )
            self.assertEquals('confluence-plugin-base', parent.artifactId)
            self.assertEquals('17', parent.version)


class Foo(object):
    """ Used in UntangleInObjectsTestCase """
    def __init__(self):
        self.doc = untangle.parse('<a><b x="1">foo</b></a>')


class UntangleInObjectsTestCase(unittest.TestCase):
    """ tests usage of untangle in classes """
    def test_object(self):
        foo = Foo()
        self.assertEquals('1', foo.doc.a.b['x'])
        self.assertEquals('foo', foo.doc.a.b.cdata)


class UrlStringTestCase(unittest.TestCase):
    """ tests is_url() function """
    def test_is_url(self):
        self.assertFalse(untangle.is_url('foo'))
        self.assertFalse(untangle.is_url('httpfoo'))
        self.assertFalse(untangle.is_url(7))
        self.assertTrue(untangle.is_url('http://foobar'))
        self.assertTrue(untangle.is_url('https://foobar'))


class TestSaxHandler(unittest.TestCase):
    """ Tests the SAX ContentHandler """

    def test_empty_handler(self):
        h = untangle.Handler()
        self.assertRaises(IndexError, h.endElement, 'foo')
        self.assertRaises(IndexError, h.characters, 'bar')

    def test_handler(self):
        h = untangle.Handler()
        h.startElement('foo', {})
        h.endElement('foo')
        self.assertEquals('foo', h.root.children[0]._name)

    def test_cdata(self):
        h = untangle.Handler()
        h.startElement('foo', {})
        h.characters('baz')
        self.assertEquals('baz', h.root.children[0].cdata)


class FigsTestCase(unittest.TestCase):
    def test_figs(self):
        doc = untangle.parse('tests/res/figs.xml')
        expected_pairs = [
            ('key1', 'value1'),
            ('key2', 'value2'),
            ('key', 'value')
        ]
        pairs = []
        for group in doc.props.children:
            for prop in group.children:
                pairs.append((prop['key'], prop.cdata))
        assert expected_pairs == pairs


class ParserFeatureTestCase(unittest.TestCase):
    """Tests adding xml.sax parser features via parse()"""

    # External DTD that will never be loadable (invalid address)
    bad_dtd_xml = """<?xml version="1.0" standalone="no" ?>
        <!DOCTYPE FOO PUBLIC "foo" "http://256.0.0.1/foo.dtd">
        <foo bar="baz" />"""

    def test_valid_feature(self):
        # xml.sax.handler.feature_external_ges -> load external general (text)
        # entities, such as DTDs
        doc = untangle.parse(self.bad_dtd_xml, feature_external_ges=False)
        self.assertEqual(doc.foo['bar'], 'baz')

    def test_invalid_feature(self):
        with self.assertRaises(AttributeError):
            untangle.parse(self.bad_dtd_xml, invalid_feature=True)

    def test_invalid_external_dtd(self):
        with self.assertRaises(IOError):
            untangle.parse(self.bad_dtd_xml, feature_external_ges=True)


if __name__ == '__main__':
    unittest.main()

# vim: set expandtab ts=4 sw=4:
