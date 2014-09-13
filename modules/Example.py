
from Module import Module

"""
This example module works like this:
<alice> !g bob
<^T-1000> I will run bob over with my gaffeltruck!
"""
class Example(Module):
    def __init__(self, parent):
        Module.__init__(self, parent, name = 'gaffel', trigger = '!g')
        return

    """
     If you need to, you can override this for a custom function, if you have
     some wierd trigger, like when a http link is posted, or someone writes a
     'bad' word.
    """
    #def on_pubmsg(self, connection, event):
    #    # Including the trigger.
    #    line = event.arguments()[0].strip()
    #
    #    # Add the line to the fifo. As soon as there is data in the fifo, the
    #    # process_line() function will be called automatically.
    #    self.fifo_append(line)
    #    return

    """
     This is the only required function you need, without it you're module won't
     do anything, it will be called as soon as a line that matched your trigger
     is posted in a channel.
    
     In this module, this function will be called as soon as someone posts
     something like the following:
     12:10:54 <@nick> !g bob

     From the fifo you only get whats after the trigger, so in this case, you
     would get only 'bob'.
    """
    def process_line(self):
        # Get the oldest entry in the fifo. Don't worry, this function will be
        # called until the fifo is empty.
        line = self.fifo_pop()

        # Send a reply to the channel where the script was triggered.
        self.send('I will run %s over with my gaffeltruck!' % line)

        return

