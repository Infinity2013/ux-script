#!/usr/bin/env python
import sys
import os
import re
from clog import clog


clog = clog()
clog.setLevel("e|v")

ALLOCATION_PATTERN = "C|%d|Allocation rate"
def calculate_mem_alloc(name):
    fd = open(name, "r")
    content = fd.readlines()
    #step 1 find pid
    pid = 0
    for log in content:
        if "bindApplication" in log:
            tmp = re.findall(r"\([\s|\d]*\)", log.strip())
            if tmp:
                pid = int(tmp[0][1:-1])
                clog.d("pid = %d" % (pid))
            else:
                clog.e("Error: Can't parse pid!")
                return
            break
    keyword = ALLOCATION_PATTERN % pid
    resList = []
    for log in content:
        if keyword in log:
            tmp = re.findall(r"\d+\.\d+", log)
            if tmp:
                ts = float(tmp[0])
                clog.d("ts = %f" % (ts))
            else:
                clog.e("Error: Can't parse ts!")
                return

            tmp = re.findall(r"\d*\\n", log)
            if tmp:
                rate = int(tmp[0][:-2])
                clog.d("rate = %d" % (rate))
            else:
                clog.e("Error: Can't parse  rate!")
                return
            resList.append([ts, rate])
    total = 0
    for i in range(1, len(resList)):
        duration = (resList[i][0] - resList[i - 1][0]) * 1000
        total += resList[i - 1][1] * duration
        clog.d("current toal = %d" % total)

    duration = resList[-1][0] - resList[0][0]
    clog.v("%s: " % name)
    clog.v("total = %d" % total)
    clog.v("duartion = %f ms" % (duration * 1000))
       


    
def main():
    if len(sys.argv) < 2:
        clog.e("Error: no args!")
        sys.exit()

    for i in xrange(1, len(sys.argv)):
        calculate_mem_alloc(sys.argv[i])
        

if __name__ == "__main__":
    main()
