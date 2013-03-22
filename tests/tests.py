#!/usr/bin/env python

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

    def test_basic_with_decl(self):
        o = untangle.parse("<?xml version='1.0'?><a><b/><c/></a>")
        self.assert_(o is not None)
        self.assert_(o.a is not None)
        self.assert_(o.a.b is not None)
        self.assert_(o.a.c is not None)

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
        self.assert_(
            template.table.tr.xsl_for_each.td.xsl_apply_templates
        )

        last_template = stylesheet.xsl_template[-1]
        self.assert_(last_template)
        self.assertEquals('m_var', last_template['match'])
        self.assertEquals(
            'compact tac formula italic',
            last_template.p['class']
        )
        self.assert_(last_template.p.xsl_apply_templates)


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
        print o.page.menu.name

if __name__ == '__main__':
    unittest.main()

# vim: set expandtab ts=4 sw=4:
