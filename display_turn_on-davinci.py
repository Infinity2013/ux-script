#!/usr/bin/env python
import os
import sys
import re
import loghelper
import adbhelper
import shutil
import subprocess

from adbhelper import getProp
from update import versioncheck
logcatcmdpattern = "adb logcat -d -v threadtime > %s.log"
dmesgcmdpattern = "adb shell dmesg > %s.dmesg"

last_start = 0
last_end = 0
DVC_PATH = "C:\Users\ggchen\Desktop\davinci\Release\DaVinci.exe"
DVC_QS = "display_on.qs"

def doDVC():
    cmd = "%s -device %s -p %s" % (DVC_PATH, device_serial(), DVC_QS)
    os.system(cmd)

def device_serial(i = 1):
    p = subprocess.Popen("adb devices", shell = True, stdout = subprocess.PIPE)
    content = p.stdout.readlines()
    if len(content) < 3:
        sys.exit()
    return content[i].strip().split()[0]
        

def main():
    versioncheck()
    if len(sys.argv) == 3:
        kernelWakeupTime = getKernelWakeupTime(sys.argv[1])
        fwWakeupTime = getFwWakeupTime(sys.argv[2])
        print ("%d + %d = %d") % (kernelWakeupTime, fwWakeupTime, kernelWakeupTime + fwWakeupTime)
        return
    mainKey = raw_input("Enter mainKey: ")
    pwd = os.getcwd()
    workpath = "%s/%s" % (pwd, mainKey)
    if os.path.exists(workpath):
        shutil.rmtree(workpath)
    os.makedirs(workpath)
    os.chdir(workpath)

    outputList = []
    index = 0


    resList = []

    releaseInfo = adbhelper.getDeviceInfo()
    resOutput = "%s(%s).res" % (mainKey, releaseInfo)
    outfd = open(resOutput, "w")

    lastkernelTime = 0
    doDVC()
    while index < 5:
        print "index %d is done!" % index
        index += 1
        outputpreffix = "%s_%d-%s" % (mainKey, index, releaseInfo)

        logcatcmd = logcatcmdpattern % (outputpreffix)
        dmesgcmd = dmesgcmdpattern % (outputpreffix)

        os.system(logcatcmd)
        os.system(dmesgcmd)

        outputpreffix = re.sub("\\\\", "", outputpreffix)
        logoutput = "%s.log" % outputpreffix
        dmesgoutput = "%s.dmesg" % outputpreffix

        fwWakeupTime = getFwWakeupTime(logoutput)
        kernelWakeupTime = getKernelWakeupTime(dmesgoutput)
        wakeupTime = kernelWakeupTime + fwWakeupTime

        outContent = "%d + %d = %d" % (kernelWakeupTime, fwWakeupTime, wakeupTime)
        print outContent
        outfd.write(outContent)
        outfd.write("\n")
        if fwWakeupTime > 0 and kernelWakeupTime > 0 and kernelWakeupTime < 1000:
            resList.append(wakeupTime)
        doDVC()

    average = sum(resList)/len(resList)
    outContent =  "average of %d results: %d" % (len(resList), average)
    print outContent
    outfd.write(outContent)
    outfd.close()
    os.chdir(pwd)

def getFwWakeupTime(logoutput):
    startpoint = 0
    endpoint = 0
    fd = open(logoutput, "r")
    logcatLogs = fd.readlines()
    for log in logcatLogs:
        logElement = loghelper.parse2Element(log, "logcat")
        if "Waking up from sleep" in logElement.tagContent:
            startpoint = logElement.ts
        elif "setPowerMode" in logElement.tagContent or "Failed to set screen crtc_id 6" in logElement.tagContent:
        #elif re.search("brightness 8\d", logElement.tagContent):
            endpoint = logElement.ts
    fwWakeupTime = endpoint - startpoint
    fd.close()
    return fwWakeupTime

def getKernelWakeupTime(dmesgoutput):
    global last_start, last_end
    startpoint = 0
    endpoint = 0
    fd = open(dmesgoutput, "r")
    dmesgLogs = fd.readlines()
    for log in dmesgLogs:
        dmesgElement = loghelper.parse2Element(log, "dmesg")
    
        if "resume from mwait" in dmesgElement.content or "Suspended for" in dmesgElement.content:
            startpoint = dmesgElement.ts
        elif "Restarting tasks" in dmesgElement.content:
            endpoint = dmesgElement.ts
    
    fd.close()
    if startpoint == last_start or endpoint == last_end:
        return 0
    else:
        last_start = startpoint
        last_end = endpoint

    kernelWakeupTime = endpoint - startpoint
    return kernelWakeupTime


if __name__ == "__main__":
    main()
