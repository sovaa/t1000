#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Module import Module

class Weather(Module):
    def __init__(self, parent):
        Module.__init__(self, parent, 'weatherforcast', '!wf')
        return

    # use the google api and try to ger weather information on the location
    def get_weather(self, line):
        import commands
        from xml.etree.ElementTree import parse, XML
        import urllib, re

        orig = line
        if not line:
            orig = line = 'Stockholm, Sweden'

        location = re.sub(' ', '+', line)
        for ch in (('å', 'a'), ('ä', 'a'), ('ö', 'o'), ('Å', 'A'),  ('Ä', 'A'), ('Ö', 'O')):
            location = re.sub(ch[0], ch[1], location)
            
        url = 'http://www.google.com/ig/api?weather=' + location + '&hl=sv'
        self.log('about to fetch: ' + url)

        xml = commands.getstatusoutput('curl --silent -L --insecure -A "Mozilla/4.73 [en] (X11; U; Linux 2.2.15 i686)" "%s"' % url)[1]
        rep = (
            ('\xc5', '\xc3\x85'), # Å
            ('\xc4', '\xc3\x84'), # Ä
            ('\xd6', '\xc3\x96'), # Ö
            ('\xe5', '\xc3\xa5'), # å
            ('\xe4', '\xc3\xa4'), # ä
            ('\xf6', '\xc3\xb6'), # ö
            ('\xa0%', ' %')       # %
        )

        rep_days = (
            ('mån', 'Måndag'),
            ('tis', 'Tisdag'),
            ('ons', 'Onsdag'),
            ('tor', 'Torsdag'),
            ('fre', 'Fredag'),
            ('lör', 'Lördag'),
            ('sön', 'Söndag')
        )

        for r in rep:
            xml = re.sub(r[0], r[1], xml)

        #dom = parse(urllib.urlopen(url)).getroot()
        elements = XML(xml).findall('weather/forecast_conditions/')
        if not elements:
            return False

        for element in elements:
            w = []
            for el in element._children:
                w.append(el.attrib['data'].encode('utf-8'))

            # replace codewords for days in week with real ones
            for r in rep_days:
                w[0] = re.sub(r[0], r[1], w[0])

            for (i, v) in enumerate(w):
                if v == '':
                    w[i] = '<okänt>'

            retval = '%s: %s, högst %s °C, lägst %s °C' % (w[0], w[4], w[2], w[1])
            self.send(retval)
            self.log(retval)
        return True

    # required function
    def process_line(self):
        line = self.fifo_pop()
        self.log('getting weather from \'%s\'' % line)

        weather = self.get_weather(line)
        if not weather:
            self.log('ERROR: could not get weather for location \'%s\'' % line)
            self.send('Could not find \'%s\'' % line)
        return

