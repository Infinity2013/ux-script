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
a = p.parse_known_args(sys.argv)

args = {}
args["repeat"] = a[0].repeat
args["sleep_time"] = a[0].slee_time
args["systrace"] = a[0].systrace
args['warm_launch'] = a[0].warm_launch
# ----------------------------------------------------------------------------------------------------


args["uiobject_name"] = "Phone"
args["layer"] = "com.android.dialer/com.android.dialer.DialtactsActivity"
args["packageName"] = "com.android.dialer"
args["outName"] = "%s(%s)-%s_%s.launch" % ("Phone", 'warm' if a[0].warm_launch else 'cold', ic.board(), ic.release())
# ----------------------------------------------------------------------------------------------------
doQALaunchTime(args)