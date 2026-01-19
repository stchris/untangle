#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import untangle
import xml.sax
from xml.sax.xmlreader import AttributesImpl

import defusedxml


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

    def test_truthiness(self):
        o = untangle.parse("<a><b/><c/></a>")
        self.assertTrue(o)
        self.assertTrue(o.a)
        self.assertTrue(o.a.b)
        self.assertTrue(o.a.c)

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

    def test_handler(self):
        h = untangle.Handler()
        h.startElement("foo", AttributesImpl({}))
        h.endElement("foo")
        self.assertEqual("foo", h.root.children[0]._name)

    def test_cdata(self):
        h = untangle.Handler()
        h.startElement("foo", AttributesImpl({}))
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
        with self.assertRaises(defusedxml.common.ExternalReferenceForbidden):
            untangle.parse(self.bad_dtd_xml)

    def test_invalid_feature(self):
        with self.assertRaises(AttributeError):
            untangle.parse(self.bad_dtd_xml, invalid_feature=True)

    def test_invalid_external_dtd(self):
        with self.assertRaises(defusedxml.common.ExternalReferenceForbidden):
            untangle.parse(self.bad_dtd_xml)


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


class TestExternalEntityExpansion(unittest.TestCase):
    def test_xxe(self):
        # from https://pypi.org/project/defusedxml/#external-entity-expansion-remote
        with self.assertRaises(defusedxml.common.EntitiesForbidden):
            untangle.parse("tests/res/xxe.xml")


class ElementNameSanitizationTestCase(unittest.TestCase):
    """Test handling of special characters in element names"""

    def test_hyphen_replacement(self):
        """Test hyphen replacement with underscore"""
        o = untangle.parse("<root><foo-bar/></root>")
        self.assertTrue(hasattr(o.root, "foo_bar"))

    def test_dot_replacement(self):
        """Test dot replacement with underscore"""
        o = untangle.parse("<root><foo.bar/></root>")
        self.assertTrue(hasattr(o.root, "foo_bar"))

    def test_colon_replacement(self):
        """Test colon replacement with underscore"""
        o = untangle.parse("<root><foo:bar/></root>")
        self.assertTrue(hasattr(o.root, "foo_bar"))

    def test_multiple_special_chars(self):
        """Test multiple special characters in same name"""
        o = untangle.parse("<root><foo-bar:baz.qux/></root>")
        self.assertTrue(hasattr(o.root, "foo_bar_baz_qux"))

    def test_conflicting_names_after_sanitization(self):
        """Test handling of names that conflict after sanitization"""
        o = untangle.parse("<root><foo-bar/><foo_bar/></root>")
        children = o.root.foo_bar
        self.assertEqual(2, len(children))


class CDataHandlingTestCase(unittest.TestCase):
    """Test CDATA handling edge cases"""

    def test_whitespace_only_cdata(self):
        """Test handling of whitespace-only CDATA"""
        o = untangle.parse("<root>   \n\t  </root>")
        self.assertEqual("   \n\t  ", o.root.cdata)

    def test_empty_cdata(self):
        """Test handling of empty CDATA"""
        o = untangle.parse("<root></root>")
        self.assertEqual("", o.root.cdata)

    def test_cdata_with_special_chars(self):
        """Test CDATA with special XML characters"""
        o = untangle.parse("<root>&lt;&gt;&amp;&quot;&apos;</root>")
        self.assertEqual("<>&\"'", o.root.cdata)

    def test_mixed_content(self):
        """Test elements with mixed text and child elements"""
        o = untangle.parse("<root>Before<child/>After</root>")
        self.assertEqual("BeforeAfter", o.root.cdata)


class LargeXmlTestCase(unittest.TestCase):
    """Test performance with large XML documents"""

    def test_large_xml_parsing(self):
        """Test parsing of large XML documents"""
        large_xml = "<root>" + "<item>data</item>" * 1000 + "</root>"
        o = untangle.parse(large_xml)
        self.assertEqual(1000, len(o.root.item))

    def test_deep_nesting(self):
        """Test parsing of deeply nested XML"""
        nested_xml = "<root>"
        for i in range(10):
            nested_xml += f"<level{i}>"
        nested_xml += "content"
        for i in range(9, -1, -1):
            nested_xml += f"</level{i}>"
        nested_xml += "</root>"

        o = untangle.parse(nested_xml)  # noqa: F841
        path = "o.root"
        for i in range(10):
            path += f".level{i}"
        path += ".cdata"
        self.assertEqual("content", eval(path))


class ErrorHandlingTestCase(unittest.TestCase):
    """Additional error handling tests"""

    def test_malformed_attributes(self):
        """Test handling of malformed attributes"""
        with self.assertRaises(xml.sax.SAXParseException):
            untangle.parse("<root attr='unclosed></root>")

    def test_duplicate_attributes(self):
        """Test handling of duplicate attributes"""
        with self.assertRaises(xml.sax.SAXParseException):
            untangle.parse("<root attr='value1' attr='value2'></root>")

    def test_invalid_xml_characters(self):
        """Test handling of invalid XML characters"""
        with self.assertRaises(xml.sax.SAXParseException):
            o = untangle.parse("<root>\x00\x01\x02</root>")
            self.assertEqual("\x00\x01\x02", o.root.cdata)


class IntegrationTestCase(unittest.TestCase):
    """Test with real-world XML formats"""

    def test_rss_feed(self):
        """Test parsing RSS feed format"""
        rss_xml = """<?xml version="1.0"?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <description>A test RSS feed</description>
        <item>
            <title>Item 1</title>
            <description>First item</description>
        </item>
        <item>
            <title>Item 2</title>
            <description>Second item</description>
        </item>
    </channel>
</rss>"""
        o = untangle.parse(rss_xml)
        self.assertEqual("Test Feed", o.rss.channel.title.cdata)
        self.assertEqual("A test RSS feed", o.rss.channel.description.cdata)
        self.assertEqual(2, len(o.rss.channel.item))
        self.assertEqual("Item 1", o.rss.channel.item[0].title.cdata)

    def test_atom_feed(self):
        """Test parsing Atom feed format"""
        atom_xml = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Example Feed</title>
    <entry>
        <title>Atom Entry</title>
        <summary>Entry summary</summary>
    </entry>
</feed>"""
        o = untangle.parse(atom_xml)
        self.assertTrue(o.feed)

    def test_svg_xml(self):
        """Test parsing SVG XML"""
        svg_xml = """<?xml version="1.0"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="40" fill="red"/>
    <rect x="10" y="10" width="30" height="30" fill="blue"/>
</svg>"""
        o = untangle.parse(svg_xml)
        self.assertEqual("100", o.svg["width"])
        self.assertEqual("100", o.svg["height"])


class UrlParsingTestCase(unittest.TestCase):
    """Enhanced URL parsing tests"""

    def test_url_scheme_variations(self):
        """Test various URL schemes"""
        self.assertTrue(untangle.is_url("http://example.com"))
        self.assertTrue(untangle.is_url("https://example.com"))
        self.assertFalse(untangle.is_url("ftp://example.com"))
        self.assertFalse(untangle.is_url("file://example.com"))

    def test_url_with_port_and_path(self):
        """Test URLs with ports and paths"""
        self.assertTrue(untangle.is_url("http://example.com:8080/path"))
        self.assertTrue(untangle.is_url("https://example.com:443/path/to/resource"))

    def test_url_authentication(self):
        """Test URLs with authentication"""
        self.assertTrue(untangle.is_url("http://user:pass@example.com"))
        self.assertTrue(untangle.is_url("https://user@example.com:8080"))

    def test_invalid_urls(self):
        """Test invalid URL formats"""
        self.assertFalse(untangle.is_url("http//example.com"))  # missing colon
        self.assertFalse(untangle.is_url("://example.com"))  # missing scheme
        self.assertFalse(untangle.is_url("example.com"))  # missing scheme


class MemoryManagementTestCase(unittest.TestCase):
    """Test memory and resource management"""

    def test_file_object_handling(self):
        """Test various file-like objects"""
        from io import BytesIO, StringIO

        # Test StringIO
        xml_content = "<root><child>test</child></root>"
        string_io = StringIO(xml_content)
        o = untangle.parse(string_io)
        self.assertEqual("test", o.root.child.cdata)

        # Test BytesIO
        bytes_io = BytesIO(xml_content.encode("utf-8"))
        o = untangle.parse(bytes_io)
        self.assertEqual("test", o.root.child.cdata)


class AttributeHandlingTestCase(unittest.TestCase):
    """Enhanced attribute handling tests"""

    def test_empty_attributes(self):
        """Test elements with empty attributes"""
        o = untangle.parse('<root attr=""></root>')
        self.assertEqual("", o.root["attr"])

    def test_attributes_with_special_chars(self):
        """Test attributes with special characters"""
        o = untangle.parse('<root attr="&lt;&gt;&amp;&quot;&apos;"></root>')
        # XML entities are automatically decoded by the parser
        self.assertEqual("<>&\"'", o.root["attr"])

    def test_attributes_with_unicode(self):
        """Test attributes with Unicode characters"""
        o = untangle.parse('<root attr="valüé ◔‿◔"></root>')
        self.assertEqual("valüé ◔‿◔", o.root["attr"])

    def test_missing_attribute_access(self):
        """Test accessing missing attributes"""
        o = untangle.parse("<root></root>")
        self.assertIsNone(o.root["missing"])
        self.assertIsNone(o.root.get_attribute("missing"))


if __name__ == "__main__":
    unittest.main()

# vim: set expandtab ts=4 sw=4
