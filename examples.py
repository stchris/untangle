#!/usr/bin/env python

import untangle


def access():
	o = untangle.parse('''<?xml version="1.0"?>
							<node id="5"><subnode value="abc"/></node>
					''')
	return "Node id = %s, subnode value = %s" % (o.node['id'], o.node.subnode['value'])

def siblings_list():
	o = untangle.parse('''<?xml version="1.0"?>
		<root><child name="child1"/><child name="child2"/><child name="child3"/></root>
					''')
	return ','.join([child['name'] for child in o.root.child])


def google_weather():
	location = raw_input('Select location to retrieve weather data for: ')
	url = 'http://www.google.com/ig/api?weather=%s' % location
	o = untangle.parse(url).xml_api_reply
	s = "Location: %s\n" % o.weather.forecast_information.city['data']
	s = s +  "Current temperature (Celsius): %s\n" % o.weather.current_conditions.temp_c['data']
	s = s + "Current temperature (Fahrenheit): %s\n" % o.weather.current_conditions.temp_f['data']
	s = s + "Forecast:\n"
	for fc in o.weather.forecast_conditions:
		s = s + "\t%s: Low %s, High: %s\n" % (fc.day_of_week['data'], fc.low['data'], fc.high['data'])
	return s

examples = [('Access children with parent.children and attributes with element["attribute"]', access),
			('Access siblings as list', siblings_list),
			('Fetch the weather from the Google Weather API and show some data', google_weather	)]

if __name__ == '__main__':
	for description, func in examples:
		print '=' * 70
		print description
		print '=' * 70
		print
		print func()
		print

