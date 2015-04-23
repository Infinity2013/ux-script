#!/usr/bin/env python
'''
some common function via adb
Copyright (C) 2014  Wu, Xiaoliang (1409300706@qq.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os
import sys
import re
import subprocess
import time
import keyword

DBG = True
tsKeyWords = ["touch", "ts", "ft5x0x"]

def killFromLRU():
    p = subprocess.Popen("adb shell getprop ro.build.version.release", shell = True, stdout = subprocess.PIPE)
    version = p.stdout.readline().strip()
    
    os.system("adb shell input keyevent 187")
    time.sleep(1)
    if "4" in version:
        os.system("adb shell input swipe 183 1096 726 1129")
    else:
        os.system("adb shell input swipe 200 674 700 674 250")
    time.sleep(1)

def root():
    subprocess.check_call("adb root", shell = True)
    time.sleep(1)
    subprocess.check_call("adb remount", shell = True)


def amstop(packageName):
    cmd = "adb shell am force-stop %s" % (packageName)
    os.system(cmd)

def getPackageVersion(packageName):
    cmd = "adb shell dumpsys package %s | grep versionName" % (packageName)
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    res = p.stdout.readline().strip()

    if res == "":
        print "Error: wrong package: %s." % packageName
        return ""

    return res.split("=")[1]


def pull(src, dst, lastest = False):
    if lastest:
        cmd = "adb shell \"ls %s\" | tail -1" % src
        p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
        res = p.stdout.readline().strip()
        if res == "":
            print "Erro: there is no files under %s." % src
            sys.exit()
        src = res
                
    cmd = "adb pull %s %s" % (src, dst)
    subprocess.check_call(cmd)

def getTSNode():
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
        isFound = False
        for keyword in tsKeyWords:
            if keyword in item:
                position = devices_info_list.index(item)
                isFound = True
                break
        if isFound:
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


def getReleaseNum():
    '''
    [saltbay-userdebug 4.4.2 KOT49H main-latest-2812 dev-keys]
    DeviceReleaseInfo[0]  release mode
    DeviceReleaseInfo[1]  release version
    DeviceReleaseInfo[2]  release name
    DeviceReleaseInfo[3]  release version incremental
    DeviceReleaseInfo[4]  unknown
    '''
    p = subprocess.Popen("adb shell getprop ro.build.description", shell = True, stdout = subprocess.PIPE)
    DeviceReleaseInfo = p.stdout.readlines()[0].split()
    
    info = ""
    if re.findall("[A-Za-z]", DeviceReleaseInfo[3]) != []:
        info = DeviceReleaseInfo[3]
    else:
        info = DeviceReleaseInfo[1]

    return info

def getBoardName():
    p = subprocess.Popen("adb shell getprop ro.product.name", shell = True, stdout = subprocess.PIPE)
    boardName = p.stdout.readlines()
    if len(boardName) > 0:
        return boardName[0].strip()
    else:
        return "Error"

def getDeviceInfo():
    releaseNum = getReleaseNum()
    boardName = getBoardName()
    releaseInfo = "%s_%s" % (boardName, releaseNum)
    return releaseInfo

def getProp(key):
    cmd = "adb shell getprop %s" % key
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    value = p.stdout.readlines()
    if len(value) > 0:
        return value[0].strip()
    else:
        print "There is no prop named: %s" % key
        return "Error"

def setProp(key, var):
    cmd = "adb shell setprop %s %s" % (key, var)
    os.system(cmd)

def getHardwareInfo():
    return getProp("ro.boot.hardware")

def getAndroidVer():
    value = getProp("ro.build.version.release")
    if value != "Error":
        if "Lolli" in value or "5" in value:
            return "l"
        else:
            return "kk"
    return value

def dumpMemInfo(packageName):
    p = subprocess.Popen("adb shell dumpsys meminfo %s" % (packageName), shell = True, stdout = subprocess.PIPE)
    info = p.stdout.readlines()
    if (len(info) == 0):
        print "Error: Couldn't get meminfo: %s" % packageName
        return None
    return info
