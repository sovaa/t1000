#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib2
import json

from Module import Module

class Wunder(Module):
    def __init__(self, parent):
        Module.__init__(self, parent, 'weather', '!w')
        return

    # use the wunderground api and try to get weather information on the location
    def get_weather(self, line):
        key = '850cecfc6a1c500e'
        default = False
    
        if not line:
            line = '/q/Lidingo,%20Sweden'
            default = True
        else:
            line = line.replace(' ', '%20')
            line = self.auto(line)

        if not line:
            self.log('no weather for: ' + line)
            return None
    
        url = 'http://api.wunderground.com/api/' + key + '/conditions' + line + '.json'
        self.log('getting weather with url: ' + url)
    
        f = urllib2.urlopen(url)
        json_string = f.read()
        j = json.loads(json_string)['current_observation']
    
        location = j['display_location']['full']
        weather = j['weather'].lower()
        temp_c = j['temp_c']
        hum = j['relative_humidity']
        wind_dir = j['wind_dir'].upper()
        wind_kph = j['wind_kph']
        feels_c = j['feelslike_c']
        precip = j['precip_today_metric']

        if default:
            location = "Stockholm, Sweden"

        return u'It\'s %s and %s °C now in %s\nWind: %s %s, relative humidity: %s, feels like %s °C, precipitation today: %s mm' %  \
            (weather, temp_c, location, wind_kph, wind_dir, hum, feels_c, precip)

    def auto(self, line):
        key = '850cecfc6a1c500e'
        url = 'http://autocomplete.wunderground.com/aq?query=' + line
        self.log('getting autocomplete for location: ' + line)
    
        f = urllib2.urlopen(url)
        json_string = f.read()
    
        j = json.loads(json_string)['RESULTS']
    
        if not j:
            return None
    
        return j[0]['l']

    # required function
    def process_line(self):
        orig = line = self.fifo_pop()
        self.log('getting weather from \'%s\'' % line)

        retries = 5
        current = 1
        weather = None

        while current < retries:
          try:
            weather = self.get_weather(line)
            break
          except:
            self.log('ERROR: could not get weather, might retry')
            current+=1
            continue

        if not weather:
            reasons = [
                'I lost my API key.',
                'I have other things to do.',
                'I don\'t like you.',
                'I love someone else.',
                'you\'re not my type.',
                'we\'re just too different. Me; an omnipotent killing machine. You; a humble meatbag.',
                'I like turtles!',
                'I\'m scared!',
                'you make me feel all fuzzy. :3',
                'tits.',
                'I just saw O\'Connor!',
                'it\'s my birthday.',
                'I\'m too tired.',
                'I don\'t want to.',
                'you don\'t deserve me.',
                'why should I?',
            ]

            from random import choice
            reason = choice(reasons)

            self.log('ERROR: could not get weather for location \'%s\'' % orig)
            self.send('Could not get weather for \'%s\', because %s' % (orig, reason))
            return

        weather = weather.split('\n')
        for w in weather:
            self.send(w.encode('utf-8'))

        return

