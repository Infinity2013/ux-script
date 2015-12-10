#!/usr/bin/env python
from argparse import ArgumentParser
import sys
from qalaunchtime import doQALaunchTime
from infocollector import collector as ic

p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author wxl')
p.add_argument('-t', default=5,  dest='slee_time', type=int, help='sleep_time')
p.add_argument('-r', default=5,  dest='repeat', type=int, help='repeat')
p.add_argument('--systrace', default='', dest='systrace', nargs='+', help='systrace tags')
a = p.parse_known_args(sys.argv)

args = {}
#args["layer"] = "com.android.mms/com.android.mms.ui.ConversationList"
#args["packageName"] = "com.android.mms"
args["layer"] = "com.android.messaging/com.android.messaging.ui.conversationlist.ConversationListActivity"
args["packageName"] = "com.android.messaging"

#args["layer"] = "com.google.android.apps.messaging/com.google.android.apps.messaging.ui.ConversationListActivity"
#args["packageName"] = "com.google.android.apps.messaging"

args["outName"] = "%s-%s_%s.launch" % ("Messaging", ic.board(), ic.release())
# args["uiobject_name"] = "Messaging"
args['uiobject_name'] = "Messenger"
args["repeat"] = a[0].repeat
args["sleep_time"] = a[0].slee_time
args["systrace"] = a[0].systrace
args["skip"] = 1
args["evallist"] = ['adb.cmd("reboot")', 'time.sleep(60)']
doQALaunchTime(args)
