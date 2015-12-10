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
args["layer"] = "com.android.gallery3d/com.android.gallery3d.app.GalleryActivity"
args["packageName"] = "com.android.gallery3d"
args["outName"] = "%s-%s_%s.launch" % ("Gallery", ic.board(), ic.release())
args["uiobject_name"] = "Gallery"
args["repeat"] = a[0].repeat
args["sleep_time"] = a[0].slee_time
args["systrace"] = a[0].systrace
doQALaunchTime(args)