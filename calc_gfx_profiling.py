#!/usr/bin/env python
import os
import sys
import re
import loghelper
from clog import clog

clog = clog()
clog.setLevel("d|e|v")

def calc_gfx_profiling(name):
    fd = open(name, "r")
    content = fd.readlines()

    index = 0
    for i in xrange(len(content)):
        if "Restarting tasks" in content[i]:
            index = i
    if (index == 0):
        clog.e("kernel didn't suspend!")
        sys.exit()
    resList = []
    stack = []
    clog.d("***** %s *****" % name)
    for i in xrange(index, len(content)):
        if "*ERROR*" in content[i]:
            logelement = loghelper.parse2Element(content[i], "dmesg")
            if "start" in logelement.content:
                stack.append(logelement)
            elif "end" in logelement.content:
                tmpelement = stack.pop()
                duration = logelement.ts - tmpelement.ts
                tagname = logelement.content.strip().split()[2]
                clog.d("%s: %d" % (tagname, duration))
                resList.append([tagname, duration])
    
    fd.close()
    return resList

def main():
    if len(sys.argv) < 2:
        clog.e("no args!")
        sys.exit()
    for i in xrange(1, len(sys.argv)):
        calc_gfx_profiling(sys.argv[i])

if __name__ == "__main__":
    main()
