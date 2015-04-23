#!/usr/bin/env python
import signal
import subprocess
import os
import threading
import re
import time
import sys
import tracehelper

from MyEnv import setMyPythonEnv
from MyEnv import getMyPythonEnv
from MyEnv import getArg
from DeviceCommon import getDeviceReleaseInfo
from argparse import ArgumentParser
from sendevent import sendEvent

DBG = False
GLTRACE = False
LOG = False
TODO = False
ASYNC = False
LAUNCH = False
GESTURE = ""
class LogThread(threading.Thread):
    finish = False
    LogList = []
    def run(self):
        self.LogList = []
        os.system("adb logcat -c")
        p = subprocess.Popen("adb logcat -v time", shell = True, stdout = subprocess.PIPE)
        while self.finish != True:
            self.LogList.append(p.stdout.readline())

    def finish(self):
        self.finish = True

    def getLog(self):
        return self.LogList

class EventThread(threading.Thread):
    inputEventFileName = ""
    def run(self):
        time.sleep(1)
        sendEvent(self.inputEventFileName)

    def setFileName(self, fileName):
        self.inputEventFileName = fileName

def killpg(pid):
    os.killpg(pid, signal.SIGTERM)

def screenRecord():
    p = subprocess.Popen("adb shell screenrecord /sdcard/a.mp4", shell = True, preexec_fn = os.setsid)
    return p.pid
    
def enableGlTrace():
    os.system("adb shell setprop debug.egl.trace systrace")
def disableGlTrace():
    os.system("adb shell setprop debug.egl.trace None")

def removeFromLRU():
    p = subprocess.Popen("adb shell getprop ro.build.version.release", shell = True, stdout = subprocess.PIPE)
    version = p.stdout.readline().strip()
    
    os.system("adb shell input keyevent 187")
    time.sleep(1)
    if "4" in version:
        os.system("adb shell input swipe 183 1096 726 1129")
    else:
        os.system("adb shell input swipe 200 674 700 674 250")
    time.sleep(1)

def startTracing(argDic):    
    if not ASYNC:
        time = argDic.get("time")
    tagKey = argDic.get("tagKey")
    mainKey = argDic.get("mainKey")
    traceOption = argDic.get("traceOption")
    if REPEATCOUNT != 0:
        gesture = argDic.get("gesture")
        repeatCount = REPEATCOUNT
        
    else:
        repeatCount = 0
        gesture = ""
        
    
    if GLTRACE:
        enableGlTrace()
    releaseInfo = getDeviceReleaseInfo()
    cmd = raw_input("Press Enter to Start")
    mainKeyIndex = 0
    outputList = ""
    psList = ""
    autoMode = False

    if repeatCount > 0:
        autoMode = True

    while repeatCount > 0 or cmd != "f":
        #init output name and cmd
        mainKeyIndex += 1
        HTMLoutputName = "%s_%s%d\(%s\).html" % (tagKey,mainKey, mainKeyIndex, releaseInfo)
        LogOutputName = "%s_%s%d.log" % (tagKey, mainKey, mainKeyIndex)
        outputList = outputList + " " + HTMLoutputName
        if ASYNC:
            systraceCmd = "adb shell atrace %s --async_start" % (traceOption)
        else:
            systraceCmd = "systrace.py %s -t %d -o %s" % (traceOption, time, HTMLoutputName)

        #start Capture Log and systrace
        if REPEATCOUNT != 0:
            event = EventThread()
            event.setFileName(gesture)
        if LOG:
            log= LogThread()
            log.setDaemon(True)
            log.start()
        
        if REPEATCOUNT != 0:
            event.start()

        
        if LAUNCH:
            pid = screenRecord()
            
        os.system(systraceCmd)

        if LAUNCH:
            killpg(pid)
            cmd = "adb pull /sdcard/a.mp4 ./%s_%s%d\(%s\).mp4" % (tagKey,mainKey, mainKeyIndex, releaseInfo)

            if DBG:
                print cmd
            os.system(cmd)
        
       
        if ASYNC:
            print ("\n")
            systraceCmd = "adb shell atrace -z --async_dump > tmp.trace"            
            cmd = raw_input("Press any key to stop tracing")
            os.system(systraceCmd)
            systraceCmd = "systrace.py --from-file=tmp.trace -o %s" % (HTMLoutputName)
            os.system(systraceCmd)
        #stop capturing log and get ps list
        if TODO:
            if exitInputFileName != "":
                playInput(exitInputFileName)
                time.sleep(1)
        if LOG:
            log.finish()
            pidList = []
            for item in log.getLog():
                pid = getPidFromLog(item)
                if pid != "" and (pid not in pidList) :
                    pidList.append(pid)
            psCmd = "adb shell ps | grep -E '%s'"  % ("|".join(pidList))

            psList = subprocess.Popen(psCmd, shell = True, stdout = subprocess.PIPE).stdout.readlines()
            memInfo = subprocess.Popen("adb shell dumpsys meminfo system_server", shell = True, stdout = subprocess.PIPE).stdout.readlines()

        #write log to file
            logOutput = open(LogOutputName, "w")
            for item in psList:
                logOutput.write(item)
            for item in memInfo:
                logOutput.write(item)
            for item in log.getLog():
                logOutput.write(item)
            logOutput.flush()
            logOutput.close()
        
        removeFromLRU()
        
        if autoMode:
            repeatCount -= 1
            if repeatCount == 0:
                break        
        else:
            cmd = raw_input("Enter f to stop or any key to continue")
    cmd = "google-chrome %s" % outputList
    subprocess.Popen(cmd, shell = True)

    #calculate launch time
    launchTimeOutputName = "%s_%s(%s).launch" % (tagKey, mainKey, releaseInfo)
    sum = 0
    resList = []
    fd = open(launchTimeOutputName, "w")
    fileList = outputList.split()
    for file in fileList:
        launchTime = tracehelper.getLaunchTime(file)
        sum += launchTime
        resList.append(launchTime)
        content = "%s: %d" % (file, launchTime)
        print content
        fd.write(content)
        fd.write("\n")

    maxRes = max(resList)
    minRes = min(resList)
    average = sum / mainKeyIndex
    content =  ("average: %d") % (average)
    print content
    fd.write(content)
    fd.write("\n")
    
    if mainKeyIndex > 2:
        sum = sum - maxRes - minRes
        middleAverage = sum / (mainKeyIndex - 2)
        content = ("middle average: %d") % (middleAverage)
        print content
        fd.write(content)
        fd.write("\n")
    
    fd.close()

    if GLTRACE:
        disableGlTrace()

    
def getArgsFromConsole():
    argDic = {}
    
    if not ASYNC:
        time = getArg("time", "int")
        argDic["time"] = time
        
    traceOption = getArg("traceOption", "str")
    argDic["traceOption"] = traceOption
         
    mainKey = getArg("mainKey", "str")
    argDic["mainKey"] = mainKey
    
    tagKey = getArg("extraTag", "str")
    argDic["tagKey"] = tagKey
    
    if REPEATCOUNT != 0:
        gesture = getArg("gesture", "str")
        argDic["gesture"] = gesture

    return argDic

def getArgsFromFile(fileName):
    fp = open(fileName, "r")
    argList = fp.readline()
    fp.close()
    
    return argList
def getPidFromLog(sample):
    res = re.findall('\(\s{0,3}\d*\)', sample)
    if len(res) != 0:
        return str(int(res[0][1:-1]))
    else:
        return ""

def main():
    global DBG;
    global GLTRACE
    global LOG
    global ASYNC
    global TODO
    global LAUNCH
    global REPEATCOUNT
    p = ArgumentParser(usage='auto.py -d -gl -log -async -todo', description='Author wxl')
    p.add_argument('-d', default=0,  dest='debug', action="store_true", help='enable debug info')
    p.add_argument('-gl', dest='gltrace', action="store_true", help='enable gltrace')
    p.add_argument('-log', dest='log', action="store_true", help='enable capture log')
    p.add_argument('-async', dest="async", action="store_true", help="capture trace async")
    p.add_argument('-todo', dest="todo", action="store_true", help="enable some test feature")
    p.add_argument('-l', dest="launch", action="store_true", help="record screen")
    p.add_argument('-r', dest="repeatcount", default=0, help="repeat times, it requires gesture")
    args = p.parse_known_args(sys.argv)

    DBG = args[0].debug
    GLTRACE = args[0].gltrace
    LOG = args[0].log
    ASYNC = args[0].async
    TODO = args[0].todo
    LAUNCH = args[0].launch
    REPEATCOUNT = int(args[0].repeatcount)
    
    if DBG:
        print ("DBG: %s, GLTRACE: %s, LOG: %s, ASYNC: %s, TODO: %s, LAUNCH: %s") % (DBG, GLTRACE, LOG, ASYNC, TODO, LAUNCH)
        
    startTracing(getArgsFromConsole())

if __name__ == '__main__':
    main()





