#!/usr/bin/env python

from argparse import ArgumentParser
import sys

from qalaunchtime import doQALaunchTime
import adbhelper
import locationmanager

pair = locationmanager.getLocation("4")
x = pair[0]
y = pair[1]

layer = "com.android.settings/com.android.settings.Settings"
packageName = "com.android.settings"
time = 2
repeatCount = 10
outputName = "Settings_LaunchTime\(%s\).launch" % (
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
doQALaunchTime(qaArgs)
