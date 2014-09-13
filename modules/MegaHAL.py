
import mh_python
import os, random
from Module import Module

class MegaHAL(Module):
    def __init__(self, parent, name = 'megahal', trigger = None):
        Module.__init__(self, parent, name, trigger)
        mh_python.initbrain()
        return

    def on_pubmsg(self, connection, event):
        self.connection = connection
        self.event = event
        text = event.arguments()[0].strip()

        try:
            nick = self.getnick()
        except:
            print 'Rehashing, so for some fucking reason, we do not have a parent reference.'
            return

        skips = ['T-2000', '^T-2000', 'Suiseiseki', 'cl-irc', 't2000']

        if event._source.split('!')[0] in skips:
            return

        if nick in text.split()[0]:
            self.event = event
            self.fifo_append((event._source, ' '.join(text.split()[1:])))
        else:
            self.fifo_append((None, text))
        return

    def process_line(self):
        data = self.fifo_pop()
        reply = None
        msg = data[1]
        if msg.split()[0].endswith(':'):
            msg = ' '.join(msg.split()[1:])

        if not data[0]:
            mh_python.learn(msg)
        else:
            reply = mh_python.doreply(msg)
        if reply:
            self.send(data[0].split('!')[0].strip() + ': ' + reply)
        mh_python.cleanup()
        
        return

