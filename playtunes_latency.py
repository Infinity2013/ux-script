#!/usr/bin/env python
import loghelper
import os
import sys
import re
import time
import subprocess
from sendevent import sendEvent

def captureLog(ofile):
    cmd = "adb logcat -d -v threadtime -s TinyAlsaAudioDevice -s RouteManager | grep -E \"(open: card|periodSize|executeUnmuteRoutingStage)\" > %d.log" % ofile
    os.system(cmd)
    cmd = "adb pull /sdcard/Latency_Test_Result.txt ./%d.app" % ofile 
    os.system(cmd)

def parseLog(ofile):
    olog = "%d.log" % ofile
    oapp = "%d.app" % ofile
    logfd = open(olog, "r")
    appfd = open(oapp, "r")
    content = logfd.readlines()
    output_index = 0
    for i in xrange(len(content)):
        if "periodSize=1536" in content[i]:
            output_index = i
            break
    input_index = 0
    for i in xrange(len(content)):
        if "periodSize=1152" in content[i]:
            input_index = i
            break


    output_open = loghelper.parse2Element(content[output_index + 1], "logcat").ts - loghelper.parse2Element(content[output_index - 1], "logcat").ts
    input_open = loghelper.parse2Element(content[input_index + 1], "logcat").ts - loghelper.parse2Element(content[input_index - 1], "logcat").ts
    logfd.close()

    '''
    Cold Playback latency  = 291 msec 

    Cold Recording latency = 220 msec
    '''
    content = appfd.readlines()
    output_app = 0
    input_app = 0
    for i in xrange(len(content)):
        if "Cold Playback latency" in content[i]:
            tmp = content[i].strip().split("=")[1].split()[0]
            if tmp == "Invalid":
                output_app = 0
            else:
                output_app = int(tmp)
        elif "Cold Recording latency" in content[i]:
            tmp = content[i].strip().split("=")[1].split()[0]
            input_app = int(tmp)
    appfd.close()
            
    return [output_app, input_app, output_open, input_open]

    
def doAppTest():
    eventpath = "%s/event/playtune_gminl.event" % sys.path[0]
    sendEvent(eventpath)
    time.sleep(40)

def doCase(ofile):
    os.system("adb logcat -c")
    doAppTest()
    captureLog(ofile)
    return parseLog(ofile)

def main():
    if (len(sys.argv) != 2):
        print "args!"
        sys.exit()

    resfile = sys.argv[1]
    index = 0
    repeat = 5
    
    resfd = open("resfile", "w")
    
    while (index < repeat):
        res = doCase(index)
        content = "index %d:\n  outpt: %d - %d = %d ms\n  input: %d - %d = %d ms\n" % (index, res[0], res[2], res[0] - res[2], res[1], res[3], res[1] - res[3])
        outputList.append(res[0] - res[2])
        intputList.append(res[1] - res[3])
        print content
        resfd.write(content)
        index += 1
    outputList.sort()
    inputList.sort()
    content = "avg:\n  output: %d\n  input: %d\n" % (outputList[len(outputList) / 2], inputList[len(inputList) / 2])
    print content
    resfd.write(content)
    resfd.close()

if __name__ == "__main__":
    main()

