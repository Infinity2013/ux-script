#!/usr/bin/env python

import os
import subprocess
import sys
import time

DBG = False

def shot():
    os.system("adb shell input keyevent 120")

def getname():
    p = subprocess.Popen("adb shell ls /sdcard/Pictures/Screenshots", shell = True, stdout = subprocess.PIPE)
    nameList = p.stdout.readlines()
    if len(nameList) < 1:
        print "Error: no files."
        sys.exit()
    if DBG:
        print nameList
    return nameList[-1].strip()

def main():
    if len(sys.argv) != 2:
        print "usage: screencapture.py newname.png"
        sys.exit()
    newname = sys.argv[1]
    shot()
    time.sleep(2)

    adbcmd = "adb pull /sdcard/Pictures/Screenshots/%s ./%s.png" % (getname(), newname)

    if DBG:
        print adbcmd
    os.system(adbcmd)


if __name__ == "__main__":
    main()
