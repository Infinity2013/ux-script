#!/usr/bin/env python

from argparse import ArgumentParser
import sys

import adbhelper
from qalaunchtime import doQALaunchTime
import locationmanager

pair = locationmanager.getLocation("4")
x = pair[0]
y = pair[1]

layer = "com.google.android.youtube/com.google.android.apps.youtube.app.WatchWhileActivity"
packageName = "com.google.android.youtube"
time = 5 
repeatCount = 10 
outputName = "Youtube_LaunchTime\(%s\).launch" % (
    adbhelper.getDeviceInfo())
qaArgs = {}
qaArgs["x"] = x
qaArgs["y"] = y
qaArgs["layer"] = layer
qaArgs["packageName"] = packageName
qaArgs["time"] = time
qaArgs["repeatCount"] = repeatCount
qaArgs["outputfile"] = outputName

p = ArgumentParser(usage='qalaunchtime.py -d -f input -o output -d delay', description='Author wxl')
p.add_argument('-m', default=0,  dest='mode', type=int, help='mode')
args = p.parse_known_args(sys.argv)
rsd = 9 
attemp = 0
while rsd > 8 and attemp < 5:
    print "attemp %d\n" % attemp
    attemp += 1
    rsd = doQALaunchTime(qaArgs)
