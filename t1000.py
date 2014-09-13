#!/usr/bin/python

import irclib
import sys
import time

events = (
    'disconnect',
    'pubmsg',
    'privmsg',
    'join',
    'kick',
    'part',
    'mode',
    'privnotice',
    'pubnotice',
    'ison',
    'users',
    'usersstart',
    'all_raw_messages',
    'namreply',
    'nick',
    'quit',
    'nicknameinuse',
)

bob = None

def poll_modules(f, connection, event):
    try:
        for module in bob.modules:
            bob.call(module, 'on_' + f, connection, event)
    except:
        try:
            bob.log('Could not call %s on module %s.' % (f, str(module)))
        except:
            print 'wow, bob is fucked'
    return

def on_pubmsg(connection, event):
    poll_modules('pubmsg', connection, event)
    return

# this is the reply from /NAMES
def on_namreply(connection, event):
    poll_modules('namreply', connection, event)
    return

def on_all_raw_messages(connection, event):
    poll_modules('all_raw_messages', connection, event)
    return

def on_privmsg(connection, event):
    poll_modules('privmsg', connection, event)
    return

def on_join(connection, event):
    poll_modules('join', connection, event)
    return

def on_users(connection, event):
    poll_modules('users', connection, event)
    return

def on_usersstart(connection, event):
    poll_modules('usersstart', connection, event)
    return

def on_part(connection, event):
    poll_modules('part', connection, event)
    return

def on_kick(connection, event):
    poll_modules('kick', connection, event)
    return

def on_quit(connection, event):
    poll_modules('quit', connection, event)
    return

def on_mode(connection, event):
    poll_modules('mode', connection, event)
    return

def on_ison(connection, event):
    poll_modules('ison', connection, event)
    return

def on_disconnect(connection, event):
    poll_modules('disconnect', connection, event)
    return

def on_privnotice(connection, event):
    poll_modules('privnotice', connection, event)
    return

def on_pubnotice(connection, event):
    poll_modules('pubnotice', connection, event)
    return

def on_nick(connection, event):
    poll_modules('nick', connection, event)
    return

def on_nicknameinuse(connection, event):
    from random import choice
    poll_modules('nicknameinuse', connection, event)

    config = bob.config
    nick = connection.get_nickname()
    if nick in config['nicknames']:
        config['nicknames'].remove(connection.get_nickname())

    nick = choice(config['nicknames'])
    bob.setnick(nick)
    connection.nick(nick)
    c = connection
    c.connect(c.server, c.port, bob.getnick())
    return

class Bot:
    def __init__(self):
        import thread
        self.config = {}
        self.actions = []
        self.connection = None
        self.nickname = None
        self.modules = []
        self.nicknames = []
        self.loglock = thread.allocate_lock()
        return

    def setnick(self, newnick):
        self.nickname = newnick
        return

    def getnick(self):
        return self.nickname

    def modules_stop(self):
        for module in self.modules:
            self.call(module, 'stop')
        return

    def rehash(self):
        import inspect, imp
        from Module import Module

        #for module in self.config['modules']:
        #    if 'modules.' + module in sys.modules:
        #        imp.reload(sys.modules['modules.' + module])
        #    else:
        #        exec 'import modules.' + module

        # kill the threads
        self.modules_stop()

        # reload config and modules
        self.modules = []
        self.config = {}
        execfile('config', {}, self.config)

        for module in self.config['modules']:
            exec 'import modules.' + module
            exec 'mod = modules.' + module
            reload(mod)

            for d in mod.__dict__:
                item = getattr(mod, d)
                if not inspect.isclass(item) or inspect.getmodule(item) != mod:
                    continue

                tempmod = item(self)
                self.modules.append(tempmod)
                self.call(tempmod, 'start')

        self.join_channels()

        return

    def call(self, c, f, *args):
        func = getattr(c, f, None)
        if callable(func):
            func(*args)
        return

    def reconnect(self, irc):
        try:
            self.connection = irc.server().connect(self.config['server'], self.config['port'], self.config['nickname'])
        except irclib.ServerConnectionError, x:
            print x
        return

    def start(self):
        execfile('config', {}, self.config)
        self.setnick(self.config['nickname'])

        try:
            int(self.config['port'])
        except ValueError:
            print "Error: Invalid port."
            sys.exit(1)

        irc = irclib.IRC()
        self.reconnect(irc)

        for event in events:
            self.connection.add_global_handler(event, eval('on_%s' % event))

        self.rehash()

        # join the channels only after we've connected
        self.connection.execute_delayed(3, self.join_channels)

        irc.process_forever()
        return

    def join_channels(self):
        for chan in self.config['channels']:
            if irclib.is_channel(chan):
                self.connection.join(chan)

if __name__ == '__main__':
    while True:
        try:
            bob = Bot()
            bob.start()
        except Exception, e1:
            try:
                bob.log(str(e1))
            except Exception, e2:
                print e2
                fh = open('fatal.log', 'a')
                fh.write(str(e2) + "\n")
            print e1
        time.sleep(5)

            


