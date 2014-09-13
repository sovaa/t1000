
from Module import Module
import sys

class APK(Module):
    def __init__(self, parent):
        Module.__init__(self, parent, name = 'apk', trigger = '!apk')
        return

    def process_line(self):
        text = self.fifo_pop()
        if len(text) < 3:
            return

        try:
            args = self.parse_input(text.split())
            self.send('APK: %.2f' % (args[0]*args[1]/args[2]))
        except Exception as inst:
            self.log('Could not parse input, or input was not numeric.')
            self.log(str(type(inst)))     # the exception instance
            self.log(str(inst.args))      # arguments stored in .args
            self.log(str(inst))           # __str__ allows args to printed directly
            pass
        return

    def parse_input(self, text):
        import re
        args = [None, None, None]

        for (i, txt) in enumerate(text):
            text[i] = re.sub(',', '.', txt)

        for arg in text:
            if '%' in arg:
                args[0] = float(arg[:-1])/100.0
            elif 'ml' in arg:
                args[1] = float(arg[:-2])
            elif 'cl' in arg:
                args[1] = float(arg[:-2])*10
            elif 'l' in arg:
                args[1] = float(arg[:-1])*1000
            elif 'kr' in arg:
                args[2] = float(arg[:-2])

        if None in args:
            if args[0] is None:
                args[0] = float(text[0])/100.0
            if args[1] is None:
                args[1] = float(text[1])
            if args[2] is None:
                args[2] = float(text[2])
            
        return args

