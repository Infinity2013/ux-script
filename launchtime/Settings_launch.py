#!/usr/bin/env python
from argparse import ArgumentParser
import sys
script_root = "%s/../" % (sys.path[0])
if script_root not in sys.path:
    sys.path.append(script_root)
from qalaunchtime import doQALaunchTime
import adbhelper

p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author wxl')
p.add_argument('-t', default=2,  dest='slee_time', type=int, help='sleep_time')
p.add_argument('-r', default=10,  dest='repeat', type=int, help='repeat')
a = p.parse_known_args(sys.argv)

args = {}
args["layer"] = "com.android.settings/com.android.settings.Settings"
args["packageName"] = "com.android.settings"
args["outName"] = "%s-%s.launch" % ("Settings", adbhelper.getDeviceInfo())
args["uiobject_name"] = "Settings"
args["repeat"] = a[0].repeat
args["sleep_time"] = a[0].slee_time
doQALaunchTime(args)
