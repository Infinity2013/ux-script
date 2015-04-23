#!/usr/bin/env python
import os
import sys
import subprocess 
import re
import math
import time
from argparse import ArgumentParser
from mail import send_email
import adbhelper
DBG = False
SLEEP_TIME_TO_BE_STABLE = 5
TAGS = "gfx wm am input view res freq dalvik"
SYSTRACE_FLAG = True 

def progressbar(current):
    barcontent = "===" * current
    content = ("[%-30s] %d/10\r") % (barcontent, current) 
    sys.stdout.write(content)
    sys.stdout.flush()

def start_tracing(tags):
    if SYSTRACE_FLAG:
        cmd = "adb shell \"atrace --async_start %s\"" % (tags)
        os.system(cmd)

def stop_tracing(out):
    if SYSTRACE_FLAG:
        cmd = "adb shell \"atrace --async_dump -z\" > out.trace"
        os.system(cmd)
        cmd = "systrace.py --from-file=out.trace -o %s" % out
        os.system(cmd)


def clearCache(package):
    cmd = "adb shell rm -rf /data/data/%s/cache" % package
    os.system(cmd)

def removeFromLRU():
    p = subprocess.Popen("adb shell getprop ro.build.version.release", shell = True, stdout = subprocess.PIPE)
    version = p.stdout.readline().strip()
    os.system("adb shell input keyevent 187")
    time.sleep(1)
#if "4" in version:
#        os.system("adb shell input swipe 183 1096 726 1129")
#    else:
    os.system("adb shell input swipe 200 674 700 674 250")
    time.sleep(1)

def amstop(packageName):
    cmd = "adb shell am force-stop %s" % packageName
    os.system(cmd)
    time.sleep(1)


'''
input:
[Info]: Gesture started at -7635284 - 134518601  (638381583516)
output:
638381583516
'''
def getStartpoint(touchscreen, x, y):
    cmd = "adb shell /data/eventHunter -i %s -g TOUCH -p %d -q %d -t B" % (touchscreen, x, y)
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    resContent = p.stdout.readline().strip()
    if re.findall("\(\d*", resContent) != []:
        resContent = resContent.split("(")[1].strip()[:-1]
    else:
        print "Error: make sure /data/eventHuner exists."
        sys.exit()
    return long(resContent)

def getEndpoint(layer):
    cmd = "adb shell dumpsys SurfaceFlinger --latency %s" % (layer)
    p = subprocess.Popen(cmd, shell = True, stdout= subprocess.PIPE)
    resContent = p.stdout.readlines()
    endpoint = 0
    length = len(resContent)
    for i in range(length):
        if re.findall("0\s*0\s*0", resContent[i]) == [] and i != 0 and i != length - 1:
            endpoint = long(resContent[i].split()[1])
            break

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
    devices_info_cmd = "adb shell cat /proc/bus/input/devices"
    p = subprocess.Popen(devices_info_cmd, shell = True, stdout = subprocess.PIPE)
    devices_info_list = p.stdout.readlines()
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
        if "touch" in item or "ts"  in item or "ft5x0x" in item:
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
def main():
    global DBG
    p = ArgumentParser(usage='qalaunchtime.py -d -f input -o output -d delay', description='Author wxl')
    p.add_argument('-d', default=0,  dest='debug', action="store_true", help='enable debug info')
    p.add_argument('-o', dest="output", default="output", help="output filename")
    p.add_argument('-f', dest="input", help = "input filename")
    p.add_argument('-t', dest="time", default = 4, help = "the time of launch")
    p.add_argument('-r', dest="repeatCount", default = 5, help = "reapeatCount")
    args = p.parse_known_args(sys.argv)

    DBG = args[0].debug
    outputfile = args[0].output
    inputfile = args[0].input
    time = int(args[0].time)
    repeatCount = int(args[0].repeatCount)


def doQALaunchTime(qaArgs):

    x = qaArgs.get("x")
    y = qaArgs.get("y")
    layer = qaArgs.get("layer")
    duration = qaArgs.get("time")
    packageName = qaArgs.get("packageName")
    repeatCount = qaArgs.get("repeatCount")
    outputName = qaArgs.get("outputfile")
    touchscreen = getTouchNode()
    outfd = open(outputName, "w")
    getLaunchTime(x, y, layer, touchscreen, duration)
#    amstop(packageName)
    removeFromLRU()

    resList = []
    index = 0
    content = "layer: %s" % layer
    print content

    while (index < repeatCount):
       # progressbar(index + 1)
        os.system("adb shell dumpsys SurfaceFlinger --latency-clear")
        start_tracing(TAGS)
        res = getLaunchTime(x, y, layer, touchscreen, duration)
        meminfo = adbhelper.dumpMemInfo(packageName)
        if meminfo != None:
            writeList(meminfo, "%s\(%d\)_%d.mem" % (outputName, res, index))
        content = "index %d: %d ms" % (index, res)
        print content
        index +=1
        resList.append(res)
#amstop(packageName)
        removeFromLRU()
#        clearCache(packageName)
        time.sleep(SLEEP_TIME_TO_BE_STABLE)
        stop_tracing("%s\(%d\)_%d.html" % (outputName, res, index))
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
    mailargs["subject"] = "%s(%s - %s) : %d ms - %d " % (packageName, adbhelper.getDeviceInfo(), adbhelper.getPackageVersion(packageName), average, rsd)
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
        squaresum += (i - average)*(i - average)
    
    SD = math.sqrt((squaresum / (n - 1)))
    RSD = (SD / average) * 100

    return RSD


if __name__ == "__main__":
    print RSD([423, 5423, 5423, 6,5 , 54277, 76,222])
