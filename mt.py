# this is a list of functions from my own mytools, which I didn't want to include in the file proper, because I want as few dependencies as possible

import re
import sys

class Logger(object):
    def __init__(self, file_name = "logfile.log"):
        self.terminal = sys.stdout
        try:
            self.log = open("logfile.log", "a")
        except:
            sys.exit("Could not create logfile {}, bailing. Try l=(file name) for an " + \
                "alternate name.".format(file_name))
        print("#################start of log")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

def list_nums(my_list, separator=', '):
    return separator.join([str(x) for x in my_list])

DASH_TO_UNDERSCORE = 1
KEEP_DASH_UNDERSCORE = 0
UNDERSCORE_TO_DASH = -1

def cfg_data_split(x, delimiter=":=", to_tuple = True, strip_line = True, dash_to_underscore = KEEP_DASH_UNDERSCORE):
    if strip_line:
        x = x.strip()
    if dash_to_underscore == DASH_TO_UNDERSCORE:
        x = x.replace("-", "_")
    if dash_to_underscore == UNDERSCORE_TO_DASH:
        x = x.replace("_", "-")
    ary = re.split("[{}]".format(delimiter), x, 1)
    if to_tuple:
        return(ary[0], ary[1])
    return ary # (prefix, data) = general usage in programs

def nohy(x, also_lower = True): # mostly for command line argument usage, so -s is -S is s is S.
    if x[0] == '-': x = x[1:]
    if also_lower:
        return x.lower()
    return x
