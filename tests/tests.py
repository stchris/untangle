#!/usr/bin/env python

import unittest
import untangle


class GoogleWeatherTestCase(unittest.TestCase):
    """ Tests parsing an XML from a URL """
    url = 'http://www.google.com/ig/api?weather=Berlin'

    def setUp(self):
        self.o = untangle.parse(self.url).xml_api_reply

    def test_city_name(self):
        city = self.o.weather.forecast_information.city['data']
        self.assertEquals('Berlin, Berlin', city)

    def test_current_temp(self):
        crt_temp = int(self.o.weather.current_conditions.temp_c['data'])
        self.assert_(crt_temp)

    def test_forecast(self):
        fc = self.o.weather.forecast_conditions
        self.assert_(len(fc) == 4)
        for f in fc:
            self.assert_(f.day_of_week['data'])
            self.assert_(f.low['data'])
            self.assert_(f.high['data'])


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
        self.assertEquals(u'1l', o.Soup.Ingredients.Water['qty'])
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
        self.assertRaises(untangle.ParseException, untangle.parse, '<unclosed>')

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
        self.assertEquals('com.atlassian.confluence.plugin.base', parent.groupId)
        self.assertEquals('confluence-plugin-base', parent.artifactId)
        self.assertEquals('17', parent.version)

        self.assertEquals('4.0.0', project.modelVersion)
        self.assertEquals('com.this.that.groupId', project.groupId)

        self.assertEquals('', project.name)
        self.assertEquals('${pom.groupId}.${pom.artifactId}', project.properties.atlassian_plugin_key)
        self.assertEquals('1.4.1', project.properties.atlassian_product_test_lib_version)
        self.assertEquals('2.9', project.properties.atlassian_product_data_version)

if __name__ == '__main__':
    unittest.main()

# vim: set expandtab ts=4 sw=4:
