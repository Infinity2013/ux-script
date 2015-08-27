#!/usr/bin/env python
from adb import adb
import subprocess
from uiautomator import device as d
import time
import os
import sys
def getstate():
    time.sleep(1)
    out = adb.cmd("shell dumpsys SurfaceFlinger").communicate()[0]
    if "isDisplayOn=1" in out:
        return True
    else:
        return False

def doCase(name):
    d.press.power()
    duration = 0
    s = getstate()
    while s is False:
        time.sleep(2)
        duration += 2
        s = getstate()
    if duration > 20:
        os.system("adb logcat -v threadtime -d > %s-%d.log" % (name, duration))
        os.system("adb shell dmesg > %s-%d.dmesg" % (name, duration))
    d.press.power()
    time.sleep(5)
    return duration

def main():
    index = 0
    d = 0
    while (d <= 20):
        print "index: %d" % index
        d = doCase(str(index))
        index += 1

if __name__ == '__main__':
    main()
