
import Fifo, thread, time

class Module(object):
    def __init__(self, parent, name, trigger = None, sleeptime = 0.5):
        self.parent = parent
        self.name = name
        self.trigger = trigger
        self.running = True
        self.sleeptime = sleeptime
        self.fifo = Fifo.Fifo()
        self.lock = thread.allocate_lock()
        self.connection = None
        self.event = None
        self.log(' '*(20-len(self.name)) + 'module loaded')
        return

    def getnick(self):
        if not self.parent:
            self.log('self.parent is None, could not get nick.')
            return ''
        return self.parent.getnick()

    def log(self, msg):
        self.parent.loglock.acquire()

        logmsg = '[%s]  %s -- %s' % (self.time_format(), self.name.upper(), msg)
        logfile = open(self.parent.config['logfile'], 'a')
        logfile.write(logmsg + '\n')
        logfile.close() 
        print logmsg

        self.parent.loglock.release()
        return

    def time_format(self):
        import time
        lt = time.localtime(time.time())
        return "%04d-%02d-%02d %02d:%02d:%02d" % (lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])

    def fifo_pop(self):
        self.lock.acquire() 
        line = self.fifo.pop()
        self.lock.release()
        return line

    def fifo_append(self, text):
        self.lock.acquire()
        self.fifo.append(text)
        self.lock.release()
        return

    def send(self, msg, target = None):
        if not self.connection or not self.event:
            self.log('ERROR: connection or event is None, could not send result')
            return

        if target == None:
            # pubmsg?
            target = self.event.target()
            if target == self.getnick(): # oh ok privmsg
                target = self.event.source().split('!')[0]

        self.connection.send_raw("PRIVMSG %s :%s" % (target, msg))
        return

    def on_privmsg(self, connection, event):
        self.on_pubmsg(connection, event)
        return

    def on_pubmsg(self, connection, event):
        if not self.trigger:
            return

        text = event.arguments()[0].strip()
        if self.trigger == text.split()[0]:
            args = None
            if len(text.split()) > 1:
                args = ' '.join(text.split()[1:])

            self.connection = connection
            self.event = event
            self.fifo_append(args)
        return

    # needs to be overridden to make the module actually do anything; this is its point of entry
    def process_line(self):
        self.log('ERROR: process_line() is not implemented')
        return

    def loop(self, string, *args):
        while self.running:
            time.sleep(self.sleeptime)
            if self.fifo.data:
                self.process_line()
        self.cleanup()
        return

    def cleanup(self):
        if self.parent:
            del self.parent
        if self.fifo:
            del self.fifo
        if self.lock:
            del self.lock
        if self.event:
            del self.event
        if self.connection:
            del self.connection
        if self:
            del self
        return

    def stop(self):
        self.running = False
        return

    def start(self):
        thread.start_new_thread(self.loop, (self.name + " module thread", 2))
        return
