#!/usr/bin/env python
import sys
from argparse import ArgumentParser

from infocollector import collector as ic
from qalaunchtime import doQALaunchTime

p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author wxl')
p.add_argument('-t', default=5,  dest='slee_time', type=int, help='sleep_time')
p.add_argument('-r', default=5,  dest='repeat', type=int, help='repeat')
p.add_argument('--systrace', default='', dest='systrace', nargs='+', help='systrace tags')
p.add_argument('-w', action='store_true', dest='warm_launch')
p.add_argument('--skip', action='store_true', dest='skip')
a = p.parse_known_args(sys.argv)

args = {}
args["repeat"] = a[0].repeat
args["sleep_time"] = a[0].slee_time
args["systrace"] = a[0].systrace
args['warm_launch'] = a[0].warm_launch
args['skip'] = a[0].skip
# ----------------------------------------------------------------------------------------------------


args["uiobject_name"] = "RocketDial"
args["layer"] = "intelgeen.rocketdial.trail/intelgeen.rocketdial.pro.RocketDial"
args["packageName"] = "intelgeen.rocketdial.trail"
args["outName"] = "%s(%s)-%s_%s.launch" % ("RocketDial", 'warm' if a[0].warm_launch else 'cold', ic.board(), ic.release())
# ----------------------------------------------------------------------------------------------------
doQALaunchTime(args)