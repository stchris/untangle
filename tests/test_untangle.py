#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import untangle
import xml


class FromStringTestCase(unittest.TestCase):
    """Basic parsing tests with input as string"""

    def test_basic(self):
        o = untangle.parse("<a><b/><c/></a>")
        self.assertTrue(o is not None)
        self.assertTrue(o.a is not None)
        self.assertTrue(o.a.b is not None)
        self.assertTrue(o.a.c is not None)
        self.assertTrue("a" in o)
        self.assertTrue("b" in o.a)
        self.assertTrue("c" in o.a)
        self.assertTrue("d" not in o.a)

    def test_basic_with_decl(self):
        o = untangle.parse("<?xml version='1.0'?><a><b/><c/></a>")
        self.assertTrue(o is not None)
        self.assertTrue(o.a is not None)
        self.assertTrue(o.a.b is not None)
        self.assertTrue(o.a.c is not None)
        self.assertTrue("a" in o)
        self.assertTrue("b" in o.a)
        self.assertTrue("c" in o.a)
        self.assertTrue("d" not in o.a)

    def test_with_attributes(self):
        o = untangle.parse(
            """
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
                     """
        )
        self.assertEqual("Tomato soup", o.Soup["name"])
        self.assertEqual(1, int(o.Soup["version"]))
        self.assertEqual("1l", o.Soup.Ingredients.Water["qty"])
        self.assertTrue(o.Soup.Instructions.add_ingredients is not None)

    def test_grouping(self):
        o = untangle.parse(
            """
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
                     """
        )
        self.assertTrue(o.root)

        children = o.root.child
        self.assertEqual(3, len(children))
        self.assertEqual("child1", children[0]["name"])
        self.assertEqual("sub1", children[0].subchild["name"])
        self.assertEqual(2, len(children[2].subchild))
        self.assertEqual("sub2", children[2].subchild[0]["name"])

    def test_single_root(self):
        self.assertTrue(untangle.parse("<single_root_node/>"))

    def test_attribute_protocol(self):
        o = untangle.parse(
            """
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
                     """
        )
        try:
            self.assertEqual(None, o.root.child.inexistent)
            self.fail("Was able to access inexistent child as None")
        except AttributeError:
            pass  # this is the expected error
        except IndexError:
            self.fail("Caught IndexError quen expecting AttributeError")

        self.assertTrue(hasattr(o.root, "child"))
        self.assertFalse(hasattr(o.root, "inexistent"))

        self.assertEqual("child1", getattr(o.root, "child")[0]["name"])

    def test_python_keyword(self):
        o = untangle.parse("<class><return/><pass/><None/></class>")
        self.assertTrue(o is not None)
        self.assertTrue(o.class_ is not None)
        self.assertTrue(o.class_.return_ is not None)
        self.assertTrue(o.class_.pass_ is not None)
        self.assertTrue(o.class_.None_ is not None)


class InvalidTestCase(unittest.TestCase):
    """Test corner cases"""

    def test_invalid_xml(self):
        self.assertRaises(xml.sax.SAXParseException, untangle.parse, "<unclosed>")

    def test_empty_xml(self):
        self.assertRaises(ValueError, untangle.parse, "")

    def test_none_xml(self):
        self.assertRaises(ValueError, untangle.parse, None)


class PomXmlTestCase(unittest.TestCase):
    """Tests parsing a Maven pom.xml"""

    def setUp(self):
        self.o = untangle.parse("tests/res/pom.xml")

    def test_parent(self):
        project = self.o.project
        self.assertTrue(project)

        parent = project.parent
        self.assertTrue(parent)
        self.assertEqual("com.atlassian.confluence.plugin.base", parent.groupId)
        self.assertEqual("confluence-plugin-base", parent.artifactId)
        self.assertEqual("17", parent.version)

        self.assertEqual("4.0.0", project.modelVersion)
        self.assertEqual("com.this.that.groupId", project.groupId)

        self.assertEqual("", project.name)
        self.assertEqual(
            "${pom.groupId}.${pom.artifactId}", project.properties.atlassian_plugin_key
        )
        self.assertEqual("1.4.1", project.properties.atlassian_product_test_lib_version)
        self.assertEqual("2.9", project.properties.atlassian_product_data_version)

    def test_lengths(self):
        self.assertEqual(1, len(self.o))
        self.assertEqual(8, len(self.o.project))
        self.assertEqual(3, len(self.o.project.parent))
        self.assertEqual(4, len(self.o.project.properties))


class NamespaceTestCase(unittest.TestCase):
    """Tests for XMLs with namespaces"""

    def setUp(self):
        self.o = untangle.parse("tests/res/some.xslt")

    def test_namespace(self):
        self.assertTrue(self.o)

        stylesheet = self.o.xsl_stylesheet
        self.assertTrue(stylesheet)
        self.assertEqual("1.0", stylesheet["version"])

        template = stylesheet.xsl_template[0]
        self.assertTrue(template)
        self.assertEqual("math", template["match"])
        self.assertEqual("compact", template.table["class"])
        self.assertEqual("compact vam", template.table.tr.xsl_for_each.td["class"])
        self.assertEqual(
            untangle.Element("", ""),
            template.table.tr.xsl_for_each.td.xsl_apply_templates,
        )

        last_template = stylesheet.xsl_template[-1]
        self.assertTrue(last_template)
        self.assertEqual("m_var", last_template["match"])
        self.assertEqual("compact tac formula italic", last_template.p["class"])
        self.assertEqual(
            untangle.Element("xsl_apply_templates", ""),
            last_template.p.xsl_apply_templates,
        )


class IterationTestCase(unittest.TestCase):
    """Tests various cases of iteration over child nodes."""

    def test_multiple_children(self):
        """Regular case of iteration."""
        o = untangle.parse("<a><b/><b/></a>")
        cnt = 0
        for i in o.a.b:
            cnt += 1
        self.assertEqual(2, cnt)

    def test_single_child(self):
        """Special case when there is only a single child element.
        Does not work without an __iter__ implemented.
        """
        o = untangle.parse("<a><b/></a>")
        cnt = 0
        for i in o.a.b:
            cnt += 1
        self.assertEqual(1, cnt)


class TwimlTestCase(unittest.TestCase):
    """Github Issue #5: can't dir the parsed object"""

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
        self.assertEqual(["Response"], dir(o))
        resp = o.Response
        self.assertEqual(["Gather", "Redirect"], dir(resp))
        gather = resp.Gather
        redir = resp.Redirect
        self.assertEqual(["Play"], dir(gather))
        self.assertEqual([], dir(redir))
        self.assertEqual(
            "http://example.com/calls/1/twiml?event=start", o.Response.Redirect.cdata
        )


class UnicodeTestCase(unittest.TestCase):
    """Github issue #8: UnicodeEncodeError"""

    def test_unicode_file(self):
        o = untangle.parse("tests/res/unicode.xml")
        self.assertEqual("ðÒÉ×ÅÔ ÍÉÒ", o.page.menu.name)

    def test_lengths(self):
        o = untangle.parse("tests/res/unicode.xml")
        self.assertEqual(1, len(o))
        self.assertEqual(1, len(o.page))
        self.assertEqual(2, len(o.page.menu))
        self.assertEqual(2, len(o.page.menu.items))
        self.assertEqual(2, len(o.page.menu.items.item))
        self.assertEqual(0, len(o.page.menu.items.item[0].name))
        self.assertEqual(0, len(o.page.menu.items.item[1].name))

    def test_unicode_string(self):
        o = untangle.parse("<Element>valüé ◔‿◔</Element>")
        self.assertEqual("valüé ◔‿◔", o.Element.cdata)

    def test_unicode_element(self):
        o = untangle.parse("<Francés></Francés>")
        self.assertTrue(o is not None)
        self.assertTrue(o.Francés is not None)


class FileObjects(unittest.TestCase):
    """Test reading from file-like objects"""

    def test_file_object(self):
        with open("tests/res/pom.xml") as pom_file:
            o = untangle.parse(pom_file)
            project = o.project
            self.assertTrue(project)

            parent = project.parent
            self.assertTrue(parent)
            self.assertEqual("com.atlassian.confluence.plugin.base", parent.groupId)
            self.assertEqual("confluence-plugin-base", parent.artifactId)
            self.assertEqual("17", parent.version)


class Foo(object):
    """Used in UntangleInObjectsTestCase"""

    def __init__(self):
        self.doc = untangle.parse('<a><b x="1">foo</b></a>')


class UntangleInObjectsTestCase(unittest.TestCase):
    """tests usage of untangle in classes"""

    def test_object(self):
        foo = Foo()
        self.assertEqual("1", foo.doc.a.b["x"])
        self.assertEqual("foo", foo.doc.a.b.cdata)


class UrlStringTestCase(unittest.TestCase):
    """tests is_url() function"""

    def test_is_url(self):
        self.assertFalse(untangle.is_url("foo"))
        self.assertFalse(untangle.is_url("httpfoo"))
        self.assertFalse(untangle.is_url(7))
        self.assertTrue(untangle.is_url("http://foobar"))
        self.assertTrue(untangle.is_url("https://foobar"))


class TestSaxHandler(unittest.TestCase):
    """Tests the SAX ContentHandler"""

    def test_empty_handler(self):
        h = untangle.Handler()
        self.assertRaises(IndexError, h.endElement, "foo")
        self.assertRaises(IndexError, h.characters, "bar")

    def test_handler(self):
        h = untangle.Handler()
        h.startElement("foo", {})
        h.endElement("foo")
        self.assertEqual("foo", h.root.children[0]._name)

    def test_cdata(self):
        h = untangle.Handler()
        h.startElement("foo", {})
        h.characters("baz")
        self.assertEqual("baz", h.root.children[0].cdata)


class FigsTestCase(unittest.TestCase):
    def test_figs(self):
        doc = untangle.parse("tests/res/figs.xml")
        expected_pairs = [("key1", "value1"), ("key2", "value2"), ("key", "value")]
        pairs = []
        for group in doc.props.children:
            for prop in group.children:
                pairs.append((prop["key"], prop.cdata))
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
        self.assertEqual(doc.foo["bar"], "baz")

    def test_invalid_feature(self):
        with self.assertRaises(AttributeError):
            untangle.parse(self.bad_dtd_xml, invalid_feature=True)

    def test_invalid_external_dtd(self):
        with self.assertRaises(IOError):
            untangle.parse(self.bad_dtd_xml, feature_external_ges=True)


class TestEquals(unittest.TestCase):
    def test_equals(self):
        a = untangle.Element("a", "1")
        b = untangle.Element("b", "1")
        self.assertTrue(a == b)

    def test_list_equals(self):
        a = untangle.Element("a", "1")
        b = untangle.Element("b", "1")
        listA = [a, b]
        c = untangle.Element("c", "1")
        self.assertTrue(c in listA)


if __name__ == "__main__":
    unittest.main()

# vim: set expandtab ts=4 sw=4:
