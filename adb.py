import subprocess
import time
import os
import sys
from clog import clog

clog = clog()
clog.setLevel("e|v|d")
class adb:
    serial = ""
    
    def __init__(self):
        print "init"

    @staticmethod
    def devices():
        p = subprocess.Popen("adb devices -l", shell = True, stdout = subprocess.PIPE)
        content = p.stdout.readlines()
        choice = 0 
        if (len(content) > 3):
            for i in xrange(1, len(content) - 1):
                print ("%d: %s" % (i, content[i].strip()))
            choice = raw_input("Please choose deivce(%d-%d): " % (1, len(content) - 2))
        elif (len(content) == 3):
            choice = 1

        if choice == 0:
            clog.e("No devices!")
            sys.exit()
        else:
            clog.d(content[choice].strip())
            return content[choice]
       
            
adb.devices()

        



