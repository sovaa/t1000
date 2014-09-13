#!/usr/bin/python

_config = {}
execfile('config', {}, _config)
for module in _config['modules']:
    exec 'import ' + module

#import Weather
#import Httptitle
#import Admin
