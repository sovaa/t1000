
from Module import Module

class Admin(Module):
    def __init__(self, parent):
        Module.__init__(self, parent, name = 'admin', trigger = None)
        self.config = {}
        execfile('config', {}, self.config)
        return

    def on_privmsg(self, connection, event):
        text = event.arguments()[0]
        (source, mask) = event._source.split('!')

        if not mask in self.config['trustedusers']:
            return

        if text == '.rehash':
            self.rehash()
        return

    def rehash(self):
        self.log('rehashing')
        self.parent.rehash()
        return
