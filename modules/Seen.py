
import Fifo, sys, time, datetime, thread
from Module import Module

class Seen(Module):
    def __init__(self, parent, name = 'seen', trigger = '!seen'):
        Module.__init__(self, parent, name, trigger)
        self.seen = {}
        self.lockdb = thread.allocate_lock()
        return

    def on_join(self, connection, event):
        connection.names(event._target)
        return

    def register_leave(self, connection, event, method):
        try:
            channel = event._target
            (nick, host) = event._source.split('!')
            nick = nick.lower()
            ptime = time.time()
    
            if channel is None:
                for chan in self.seen:
                    if self.seen[chan].has_key(nick):
                        self.seen[chan][nick] = (ptime, method, chan, host)
    
            if nick[0] in "@%+":
                nick = nick[1:]
            if self.seen.has_key(channel):
                self.seen[channel][nick] = (ptime, method, channel, host)
            else:
                self.seen[channel] = {nick: (ptime, method, channel, host)}
    
            self.save_to_db()
            if event._target:
                connection.names(event._target)
        except:
            self.log('Could not register leave.')
        return

    def on_part(self, connection, event):
        self.register_leave(connection, event, 'part')
        return

    def on_quit(self, connection, event):
        self.register_leave(connection, event, 'quit')
        return

    def on_disconnect(self, connection, event):
        self.register_leave(connection, event, 'disconnect')
        return

    def on_kick(self, connection, event):
        self.register_leave(connection, event, 'kick')
        return

    def on_namreply(self, connection, event):
        nicks = event._arguments[2][:-1].split(' ')
        channel = event._arguments[1]
        for nick in nicks:
            nick = nick.strip()
            if nick[0] in "@%+":
                nick = nick[1:]
            if self.seen.has_key(channel):
                host = None
                if self.seen[channel].has_key(nick):
                    host = self.seen[channel][nick][3]
                self.seen[channel][nick.strip()] = (None, None, channel, host)
            else:
                self.seen[channel] = {nick.strip(): (None, None, channel, None)}
        self.save_to_db()
        return

    def on_nick(self, connection, event):
        (nick, host) = event._source.split('!')
        nick = nick.lower()
        for channel in self.seen:
            if self.seen[channel].has_key(nick):
                self.seen[channel][nick] = (time.time(), 'nickchange', channel, host)
        self.save_to_db()
        connection.names(event._target)
        return

    def save_to_db(self):
        self.lockdb.acquire() 
        file = open('modules/seen.db', 'w')
        file.write('self.seen = ' + str(self.seen))
        file.close()
        self.lockdb.release()
        return

    def restore_from_db(self):
        self.lockdb.acquire() 
        execfile('modules/seen.db')
        self.lockdb.release()
        return

    def process_line(self):
        line = self.fifo_pop()
        nick = line.split(' ')[0].lower() # if more nicks specified, ignore them
        channel = self.event._target

        if self.seen.has_key(channel) and self.seen[channel].has_key(nick):
            if self.seen[channel][nick][0] is None:
                if self.seen[channel][nick][1] is None:
                    self.send('%s is here now!' % nick)
                else: # nickchange?
                    host = self.seen[channel][nick][3]
                    new_time = self.seen[channel][nick][0]
                    new_nick = None
                    for user in self.seen[channel]:
                        if self.seen[channel][user][3] == host and self.seen[channel][user][1] == None:
                            new_nick = user
                            new_time = self.seen[channel][user][0]
                            new_reason = self.seen[channel][user][1]
                            break
                    if new_nick is None:
                        self.send('I do not know what happened to %s.' % nick)
                    else:
                        self.send('%s is here using the nick %s.' % (nick, new_nick))
            else:
                # time method channel host
                host = self.seen[channel][nick][3]
                new_time = self.seen[channel][nick][0]
                new_nick = None
                new_reason = self.seen[channel][nick][1]
                for user in self.seen[channel]:
                    if self.seen[channel][user][3] == host and self.seen[channel][user][0] > new_time:
                        new_nick = user
                        new_time = self.seen[channel][user][0]
                        new_reason = self.seen[channel][user][1]
                
                new_time = time.strftime("%Y-%m-%d, %H:%M:%S", time.localtime(new_time))
                if new_nick is None:
                    self.send('I last saw %s at %s (%s).' % (nick, new_time, new_reason))
                else:
                    self.send('I last saw %s at %s using the nick %s (%s).' % (nick, new_time, new_nick, new_reason))
        else:
            self.send('I have not seen %s.' % nick.lower())
        return

    def loop(self, string, *args):
        self.restore_from_db()
        loops = 0
        while self.running:
            loops += 1
            if loops % 120 == 0:
                loops = 0
                if self.connection:
                    for channel in self.parent.config['channels']:
                        self.connection.names(channel)

            time.sleep(self.sleeptime)
            if self.fifo.data:
                self.process_line()
        return

