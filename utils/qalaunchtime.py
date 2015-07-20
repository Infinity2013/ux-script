#!/usr/bin/env python
import os
import sys
import subprocess
import re
import math
import time
from mail import send_email
from adb import adb
from infocollector import collector as ic
from mysqlwrapper import wrapper as sw
from uiautomator import device as d
from pprint import pprint
DBG = False
SLEEP_TIME_TO_BE_STABLE = 5
TAGS = "gfx wm am input view freq dalvik"
SYSTRACE_FLAG = True

'''
cur = os.getcwd()
systrace = cur/systrace
logcat = cur/logcat
dmesg = cur/dmesg
'''
work_path_dict = {}

def checkandcreate(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    return

def init_dir():
    global work_path_dict
    work_path_dict['cur'] = os.getcwd()
    work_path_dict['systrace'] = "%s/systrace" % work_path_dict.get('cur')
    work_path_dict['logcat'] = "%s/logcat" % work_path_dict.get('cur')
    work_path_dict['dmesg'] = "%s/dmesg" % work_path_dict.get('cur')
    for key in work_path_dict.keys():
        if key != 'cur':
            checkandcreate(work_path_dict.get(key))


def dump_logcat(name):
    os.chdir(work_path_dict.get('logcat'))
    with open(name, "w") as f:
        f.write(adb.cmd("logcat -v threadtime -d").communicate()[0])
    os.chdir(work_path_dict.get('cur'))


def clear_logcat():
    adb.cmd("locat -c").communicate()

def dump_dmesg(name):
    os.chdir(work_path_dict.get('dmesg'))
    with open(name, "w") as f:
        f.write(adb.cmd("shell dmesg").communicate()[0])
    os.chdir(work_path_dict.get('cur'))


def get_coordinate_precision():
    precision = {}
    out = adb.cmd("shell dumpsys input").communicate()[0].splitlines()
    for line in out:
        if "XPrecision" in line:
            precision['x'] = float(line.split(":")[-1])
        elif "YPrecision" in line:
            precision['y'] = float(line.split(":")[-1])
        else:
            continue
    return precision


def start_tracing(tags):
    if SYSTRACE_FLAG:
        adb.cmd("shell \"atrace %s --async_start\"" % (tags)).communicate()


def stop_tracing(out):
    if SYSTRACE_FLAG:
        os.chdir(work_path_dict.get('systrace'))
        with open("out.trace", "w") as f:
            f.write(adb.cmd("shell \"atrace --async_dump -z\"").communicate()[0])
        cmd = "systrace.py --from-file=out.trace -o %s" % out
        os.system(cmd)
        os.chdir(work_path_dict.get('cur'))

def removeFromLRU():
    adb.cmd("shell input keyevent 187").communicate()
    time.sleep(1)
    adb.cmd("shell input swipe 200 674 700 674 250").communicate()
    time.sleep(1)


def amstop(packageName):
    adb.cmd("shell am force-stop %s" % packageName).communicate()
    time.sleep(1)


def getStartpoint(touchscreen, x, y):
    out = adb.cmd("shell /data/eventHunter -i %s -g TOUCH -p %d -q %d -t B" % (
        touchscreen, x, y)).communicate()[0].splitlines()[0].strip()
    if re.findall("\(\d*", out) != []:
        out = out.split("(")[1].strip()[:-1]
    else:
        print "Error: make sure /data/eventHuner exists."
        sys.exit()
    return long(out)


def getEndpoint(layer):
    resContent = adb.cmd("shell dumpsys SurfaceFlinger --latency %s" % (layer)).communicate()[0].splitlines()
    endpoint = 0
    length = len(resContent)
    firstFrameIdx = 0
    for i in range(length):
        if re.findall("0\s*0\s*0", resContent[i]) == [] and i != 0 and i != length - 1:
            endpoint = long(resContent[i].split()[1])
            firstFrameIdx = i
            break
    if long(resContent[firstFrameIdx - 1].split()[0]) != 0:
        print "Warning: firatFrame is gone!"
    return endpoint


def getLaunchTime(x, y, layer, touchscreen, duration):
    startpoint = getStartpoint(touchscreen, x, y)
    time.sleep(duration)
    endpoint = getEndpoint(layer)
    if DBG:
        print ("start: %d, end: %d") % (startpoint, endpoint)
    launchtime = endpoint - startpoint
    launchtime /= 1000 * 1000

    return launchtime


def getTouchNode():
    devices_info_list = adb.cmd("shell cat /proc/bus/input/devices").communicate()[0].splitlines()
    '''
    something like this
    I: Bus=0018 Vendor=0000 Product=0000 Version=0000
    N: Name="r69001-touchscreen"
    P: Phys=
    S: Sysfs=/devices/pci0000:00/0000:00:09.2/i2c-7/7-0055/input/input0
    U: Uniq=

    B: PROP=0
    B: EV=9
    B: ABS=6608000 0
    '''
    position = 0

    for item in devices_info_list:
        if "touch" in item or "ts" in item or "ft5x0x" in item:
            position = devices_info_list.index(item)
            break
    '''
    parse the below string to get the event0
    H: Handlers=event0
    '''
    if position != 0:
        while True:
            handler_info = devices_info_list[position]
            touch_event_position = re.findall('event\d', handler_info)
            if touch_event_position != []:
                touch_postion = "/dev/input/%s" % touch_event_position[0]
                break
            position += 1
        return touch_postion
    else:
        print "Error: counldn't find touch pos!"
        return None

def killproc(t, pname):
    if t not in ["lru", "amstop"]:
        raise ValueError("%s is not supported" % t)
    if t == "lru":
        removeFromLRU()
    elif t == "amstop":
        amstop(pname)

def get_coordinate(uiobject_name):
    bounds = d(text=uiobject_name).info.get("bounds")
    x = (bounds.get("left") + bounds.get("right")) / 2
    y = (bounds.get("top") + bounds.get("bottom")) / 2
    x = x * get_coordinate_precision().get('x')
    y = y * get_coordinate_precision().get('y')
    return x, y

def doQALaunchTime(qaArgs):
    uiobject_name = qaArgs.get("uiobject_name")
    
    layer = qaArgs.get("layer")
    duration = qaArgs.get("sleep_time")
    packageName = qaArgs.get("packageName")
    repeatCount = qaArgs.get("repeat")
    outputName = qaArgs.get("outName")
    systrace = qaArgs.get("systrace", "")
    evallist = qaArgs.get("evallist")
    finishtype = qaArgs.get("finishtype", "amstop")
    time_for_stable = qaArgs.get("stabletime", 5)
    global SYSTRACE_FLAG, TAGS
    if systrace != "":
        TAGS = " ".join(systrace)
    elif systrace == ["0"]:
        SYSTRACE_FLAG = False
    touchscreen = getTouchNode()
    outfd = open(outputName, "w")
    if qaArgs.get("skip") == None:
        x, y = get_coordinate(uiobject_name)
        getLaunchTime(x, y, layer, touchscreen, duration)
        killproc(finishtype, packageName)

    resList = []
    index = 0
    content = "layer: %s" % layer
    print content
    init_dir()

    while (index < repeatCount):
        adb.cmd("shell dumpsys SurfaceFlinger --latency-clear")
        clear_logcat()
        if evallist != None:
            for line in evallist:
                eval(line)
        start_tracing(TAGS)
        dbinfo = ic.collect(packageName)
        dbinfo['name'] = packageName.split(".")[-1]  # i.e com.android.settings name: settings
        x, y = get_coordinate(uiobject_name)
        res = getLaunchTime(x, y, layer, touchscreen, duration)
        dbinfo["value"] = res
        content = "index %d: %d ms" % (index, res)
        print content
        index += 1
        resList.append(res)
        killproc(finishtype, packageName)
        url = "%s/%s(%d)_%d.html" % (os.getcwd(), outputName, res, index)
        if SYSTRACE_FLAG is True:
            dbinfo["url"] = url
        sw.insert("launch", dbinfo)
        stop_tracing("%s\(%d\)_%d.html" % (outputName, res, index))
        dump_logcat("%s\(%d\)_%d.logcat" % (outputName, res, index))
        dump_dmesg("%s\(%d\)_%d.dmesg" % (outputName, res, index))
        time.sleep(time_for_stable)

    outfd.write(content)
    outfd.write("\n")

    mailmsg = []
    sum = 0
    average = 0
    for i in range(len(resList)):
        sum += resList[i]
        content = "index %d: %d ms" % (i, resList[i])
        mailmsg.append(content)
        outfd.write(content)
        outfd.write("\n")
    average = sum / len(resList)
    content = "average: %d ms" % (average)
    mailmsg.append(content)
    print content
    outfd.write(content)
    outfd.write("\n")

    resList.sort()
    content = "median = %d ms" % (resList[(len(resList) + 1) / 2])
    mailmsg.append(content)
    print content
    outfd.write(content)
    outfd.write("\n")

    outfd.close()

    rsd = RSD(resList)

    mailmsg = ("<br/>").join(mailmsg)
    mailargs = {}
    mailargs["msg"] = mailmsg
    mailargs["subject"] = "%s(%s_%s - %s) : %d ms - %d " % (packageName,
            ic.board(), ic.release(), ic.pversion(packageName), average, rsd)
    send_email(mailargs)

    return rsd


def writeList(l, out):
    fd = open(out, "w")
    for item in l:
        fd.write(item)
    fd.close()


def RSD(arr):
    n = len(arr)
    sum = 0
    for i in arr:
        sum += i
    average = sum / n

    squaresum = 0

    for i in arr:
        squaresum += (i - average) * (i - average)

    SD = math.sqrt((squaresum / (n - 1)))
    RSD = (SD / average) * 100

    return RSD
