#!/usr/bin/python
import os
import sys
import loghelper
import time
import adbhelper
import subprocess
import re
from argparse import ArgumentParser
from clog import clog
from datetime import datetime
from update import versioncheck

TIME_TO_STABLE = 2 
INTERVAL_SLEEP = 5
clog = clog()
clog.setLevel("v|e")

def generateDefaultOutpreffix():
    #2015-04-16 14:48:32.670956
    now = str(datetime.now()).strip().split()
    date_info = now[0].split("-")
    time_info = now[1].split(":")

    outpreffix = "%s%s_%s_%s_%s" % (date_info[1], date_info[2], time_info[0], time_info[1], time_info[2][:2])
    
    return outpreffix
    
def triggerPowerBn():
    cmd = "adb shell input keyevent 26"
    os.system(cmd)
    time.sleep(TIME_TO_STABLE)

def clearLogcat():
    cmd = "adb logcat -c"
    os.system(cmd)

def dumpLogcat(outfile):
    cmd = "adb logcat -v threadtime -d > %s" % outfile
    os.system(cmd)

def calc_panel_on_off(infile):
    fd = open(infile, "r")
    content = fd.readlines()
    fd.close()
    startpoint = 0
    endpoint = 0 
    for i in xrange(len(content)): 
        # SurfaceFlinger: Set power mode=2, type=0 flinger=0xf685c000
        if "SurfaceFlinger: Set power mode" in content[i]:
            startpoint = loghelper.parse2Element(content[i], "logcat")
        #hwc     : Failed to set screen crtc_id 6, enable 1  ret -1/Invalid argument 
        elif "Failed to set screen crtc_id" in content[i]: endpoint = loghelper.parse2Element(content[i], "logcat")
        #LightsService: Excessive delay setting light: 362ms
        elif "LightsService: Excessive delay setting light" in content[i]:
            endpoint = loghelper.parse2Element(content[i], "logcat")

    res = endpoint.ts - startpoint.ts
    return res

def getPanelStateBasedOnBrightness():
    cmd = "adb shell \"cat /sys/class/backlight/intel_backlight/actual_brightness\""
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    consolelog = p.stdout.readlines()
    if len(consolelog) != 1:
        clog.e("Counldn't get brightness!")
        sys.exit()
    val = int(consolelog[0].strip())
    if val == 0:
        return "off"
    else:
        return "on"
        
#for sofia only
def getPanelStateBasedOnLog():
    clearLogcat()
    triggerPowerBn()
    time.sleep(TIME_TO_STABLE)
    cmd = "adb logcat -d"
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    content = p.stdout.readlines()
    state = "off"
    for log in content:
        if "Unblocked screen" in log:
            state = "on"
            break
    return state
            
def doCase(outfile):
    if getPanelStateBasedOnBrightness() != "off":
        triggerPowerBn()
        if getPanelStateBasedOnBrightness() != "off":
            clog.e("Counldn't power off the panel")
            sys.exit()
    clearLogcat()
    triggerPowerBn()
    dumpLogcat(outfile)
    return calc_panel_on_off(outfile)

#for sofia
def doCase4Sofia(outfile):
    attemp = 0
    while (getPanelStateBasedOnLog() != "off" and attemp < 5):
        attemp += 1
    if attemp == 5:
        clog.e("Couldn't make panel state right after 5 attemps!")
        sys.exit()
    clearLogcat()
    triggerPowerBn()
    dumpLogcat(outfile)
    fd = open(outfile, "r")
    content = fd.readlines()
    for i in xrange(len(content)):
        if "setPowerMode" in content[i]:
            pg = re.findall(r"\d+ms", content[i])
            if pg == None:
                clog.e("Couldn't parse %s!" % (content[i].strip()))
            else:
                return int(pg[0][:-2])
                

    
def main():
    versioncheck()
    p = ArgumentParser(usage='sendevent.py -r -o outfile', description='Author wxl')
    p.add_argument('-r', default=5,  dest='repeat', type=int, help='test count')
    p.add_argument('-o', dest="outpreffix", help="all the log will be stored under it", default="defaultname")
    args = p.parse_known_args(sys.argv)

    outpreffix = args[0].outpreffix
    repeat = args[0].repeat

    if outpreffix == "defaultname":
        outpreffix = generateDefaultOutpreffix() 

    pwd = os.getcwd() 
    workpath = "%s/%s" % (pwd, outpreffix) 
    if os.path.exists(workpath): 
        cmd = "rm -rf %s" % workpath 
        os.system(cmd) 
    os.makedirs(workpath) 
    os.chdir(workpath) 
    
    releaseInfo = adbhelper.getDeviceInfo()

    resfile = "%s.res" % (outpreffix)
    resfd = open(resfile, "w")
    resList = []
    index = 0
    
    while(index < repeat):
        outfile = "%s_%s_%d.log" % (outpreffix, releaseInfo, index)
        platform = adbhelper.getProp("ro.board.platform")
        res = 0
        if platform != None and "sofia" in platform:
            res = doCase4Sofia(outfile)
        else:           
            res = doCase(outfile)
        log = "index %d: %d" % (index, res)
        clog.v(log)
        resfd.write(log)
        resfd.write("\n")
        resList.append(res)
        index += 1
        time.sleep(INTERVAL_SLEEP)

    resList.sort()
    log = "middle val: %d" % (resList[len(resList) / 2])
    clog.v(log)
    resfd.write(log)
    resfd.write("\n")

    resfd.close()

if __name__ == '__main__':
    main()
