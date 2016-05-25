#!/usr/bin/env python
import os
import re
import shutil
import sys

import loghelper
from adb import adb
from infocollector import collector as ic

logcatcmdpattern = "adb logcat -d -v threadtime > %s.log"
dmesgcmdpattern = "adb shell dmesg > %s.dmesg"

last_start = 0
last_end = 0

def enable_debug(flag):
    if flag == 0:
        adb.cmd("shell 'echo 0 > /sys/power/pm_print_times'")
    else:
        adb.cmd("shell 'echo 1 > /sys/power/pm_print_times'")


def main():
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

    releaseInfo = "%s_%s" % (ic.board(), ic.release())
    resOutput = "%s(%s).res" % (mainKey, releaseInfo)
    outfd = open(resOutput, "w")

    lastkernelTime = 0
    cmd = raw_input("Enter any key to start.")
    if sys.argv[1] == "1":
        adb.cmd("shell \"echo -n 'file leds-pmic.c +p' > /d/dynamic_debug/control\"")
    while cmd != "f":
        index += 1
        outputpreffix = "%s_%d-%s" % (mainKey, index, releaseInfo)

        logcatcmd = logcatcmdpattern % (outputpreffix)
        dmesgcmd = dmesgcmdpattern % (outputpreffix)

        os.system(logcatcmd)
        os.system('adb logcat -c')
        os.system(dmesgcmd)

        outputpreffix = re.sub("\\\\", "", outputpreffix)
        logoutput = "%s.log" % outputpreffix
        dmesgoutput = "%s.dmesg" % outputpreffix

        if (sys.argv[1] == "1"):
            wakeup_time = get_wakup_time_from_dmesg(dmesgoutput)
            kernel_time = getKernelWakeupTime(dmesgoutput)
            console_log =  "wakeup_time: %d(%d)" % (wakeup_time, kernel_time)
            print console_log
            outfd.write(console_log)
            outfd.write("\n")
            if wakeup_time != 0:
                resList.append(wakeup_time)
        else:
            fwWakeupTime = getFwWakeupTime(logoutput)
            kernelWakeupTime = getKernelWakeupTime(dmesgoutput)
            wakeupTime = kernelWakeupTime + fwWakeupTime

            outContent = "%d + %d = %d" % (kernelWakeupTime, fwWakeupTime, wakeupTime)
            print outContent
            outfd.write(outContent)
            outfd.write("\n")

            if fwWakeupTime > 0 and kernelWakeupTime > 0 and kernelWakeupTime < 1000:
                resList.append(wakeupTime)
        cmd = raw_input("Press any key to continue or f to stop.")

    average = sum(resList)/len(resList)
    outContent =  "average of %d results: %d" % (len(resList), average)
    print outContent
    outfd.write(outContent)
    outfd.close()
    os.chdir(pwd)
    enable_debug(0)

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

        if "Enabling non-boot CPUs" in dmesgElement.content or "Suspended for" in dmesgElement.content:
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


def get_wakup_time_from_dmesg(dmesgoutput):
    start, end = 0, 0
    fd = open(dmesgoutput, "r")
    dmesg_list = fd.readlines()
    fd.close()
    for log in dmesg_list:
        if "Enabling non-boot CPUs" in log or "Suspended for" in log:
            start = loghelper.parse2Element(log, "dmesg").ts
    for log in dmesg_list:
        if "pmic_led_on" in log:
            end = loghelper.parse2Element(log, "dmesg").ts
            if end > start:
                break

    wakup_time = end - start
    return wakup_time

if __name__ == "__main__":
    main()
