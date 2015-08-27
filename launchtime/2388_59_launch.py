#!/usr/bin/env python
from argparse import ArgumentParser
import sys
from qalaunchtime import doQALaunchTime
from infocollector import collector as ic

p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author wxl')
p.add_argument('-t', default=5,  dest='slee_time', type=int, help='sleep_time')
p.add_argument('-r', default=10,  dest='repeat', type=int, help='repeat')
p.add_argument('--systrace', default='', dest='systrace', nargs='+', help='systrace tags')
a = p.parse_known_args(sys.argv)

args = {}
args["layer"] = "com.android.dialer/com.android.incallui.InCallActivity"
args["packageName"] = "com.android.contacts"
args["outName"] = "%s-%s_%s.launch" % ("2388_59", ic.board(), ic.release())
args["uiobject_name"] = "857-419-154"
args["repeat"] = a[0].repeat
args["sleep_time"] = a[0].slee_time
args["systrace"] = a[0].systrace
args["skip"] = 1
args["evallist"] = ['adb.cmd("shell am start com.android.contacts/.activities.PeopleActivity")', 'd(text="ahkubxt").click()', 'time.sleep(2)']
args["end_evallist"] = ['d(resourceId="com.android.dialer:id/floating_end_call_action_button").click()', 'time.sleep(20)']
doQALaunchTime(args)
