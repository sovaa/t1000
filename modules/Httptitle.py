# -*- coding: utf-8 -*-

from Module import Module

class Httptitle(Module):
    def __init__(self, parent, name = 'httptitle', trigger = None):
        Module.__init__(self, parent, name, trigger)
        return

    # override since we're not using an ordinary trigger
    def on_pubmsg(self, connection, event):
        self.event = event
        self.connection = connection
        text = event.arguments()[0].strip()
        if text.startswith('http://') or text.startswith('https://'):
            self.fifo_append(text)
        return
    
    def get_http_title(self, url):
        import commands, sys, urllib2
        allow = ('text')
        tags = (('<title>', '</title>'), ('<TITLE>', '</TITLE>'))

        url = url.split(' ')[0]
        url = url.split('#')[0]
        self.log('url is %s' % url)

        try:
            type = urllib2.urlopen(url).info().getheader('Content-Type')
            if type.split('/')[0] not in allow:
                self.log('Content type "%s" not allowed, skipping' % type)
                return
        except:
            self.log('Could not get content type: %s' % sys.exc_info()[1])
            return

        try:
            t = commands.getstatusoutput(
                'curl --silent -L --insecure -A "Mozilla/4.73 [en] (X11; U; Linux 2.2.15 i686)" "%s"' % url
            )[1]
            for (opentag, closetag) in tags:
                if opentag in t and closetag in t:
                    return self.unescape(t[ t.find(opentag)+7 : t.find(closetag) ])
        except:
            self.log('Could nog get title from URL: %s' % sys.exc_info()[1])
            pass
        return

    def unescape(self, title):
        import re
        repls = (
            ('\t', ' '),
            ('\n', ' '),
            ('[ ]+', ' '),
        )
        for rep in repls:
            title = re.sub(rep[0], rep[1], title)
        return title

    def process_line(self):
        line = self.fifo_pop()
        title = self.get_http_title(line)

        if title:
            self.log('title: ' + title)
            self.send('Title: ' + title)
        else:
            self.log('ERROR: could not get title')
        return

