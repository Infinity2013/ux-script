#!/usr/bin/env python

import re
import os
import sys
import subprocess
import time

PARSE_DBG = False 
'''
equicksearchbox-2525  ( 2525) [000] ...1 10007.451469: tracing_mark_write: B|2525|activityPause\n\
'''
class TraceElement():
    ts = 0
    pid = 0
    flag = ""
    tagName = ""
    def __init__(self, ts, pid, flag, tagName):
        self.ts = ts
        self.pid = pid
        self.flag = flag
        self.tagName = tagName

    def dump(self):
        if self.ts == -1 or self.pid == -1 or self.flag == "wrong" or self.tagName == "wrong":
            return
        print ("ts: %d, pid = %d, flag: %s, tagName: %s") % (self.ts, self.pid, self.flag, self.tagName)

class DmesgElement():
    ts = 0
    content = ""
    def __init__(self, ts, content):
        self.ts = ts
        self.content = content

    def dump(self):
        print ("[%f] %s") % (self.ts,self.content)

class LogcatElement():
    ts = 0
    pid = 0
    tid = 0
    tagType = ""
    tagName = ""
    tagContent = ""
    def __init__(self, ts, pid, tid, tagType, tagName, tagContent):
        self.ts = ts
        self.pid = pid
        self.tid = tid
        self.tagType = tagType
        self.tagName = tagName
        self.tagContent = tagContent

    def dump(self):
        print self.ts
        print self.pid
        print self.tid
        print self.tagType
        print self.tagName
        print self.tagContent

def parse2Element(log, type):
    if type == "trace":
        return parse2TraceElement(log)
    elif type == "logcat":
        return parse2LogcatElement(log)
    elif type == "dmesg":
        return parse2DmesgElement(log)
    else:
        print "Error: unsupported type %s" % type
        sys.exit()
'''
pattern:
01-02 17:58:35.603  1982  2395 W SurfaceFlinger: Timed out waiting for hw vsync; faking it
'''
def parse2LogcatElement(logcatLog):
    if not re.search("\d*:\d*:\d*.\d*", logcatLog):
        return LogcatElement(0, 0, 0, "", "", "")
    splitList =logcatLog.strip().split()

    ts = 0
    tsList = splitList[1].split(":")
    hour = int(tsList[0])
    minute = int(tsList[1])
    second = int(tsList[2].split(".")[0])
    milliseccond = int(tsList[2].split(".")[1])
    ts = (hour * 3600 + minute * 60 + second) * 1000 + milliseccond

    pid = 0
    pid = int(splitList[2])

    tid = 0
    tid = int(splitList[3])

    tagType = ""
    tagName = splitList[4]

    tagName = ""
    tagName = splitList[5][:-1]

    tagContent = " ".join(splitList[6:])

    return LogcatElement(ts, pid, tid, tagType, tagName, tagContent)


def parse2DmesgElement(dmesgLog):
    ts = -1
    res = re.search("\[[0-9\s.]*\]", dmesgLog)
    if res:
        if PARSE_DBG:
            print res.group(0)
        ts = int(float(res.group(0)[1:-1]) * 1000)
    else:
        return DmesgElement(0, "")

    content = ""
    index = dmesgLog.index("]") + 2
    content = dmesgLog[index:].strip()

    if PARSE_DBG:
        if ts == -1 or content == "":        
            print "Error: can't parse %s" % dmesgLog
            sys.exit()

    return DmesgElement(ts, content)

def parse2TraceElement(traceLog):
    if re.search("\S*-[0-9]*\s*\([\s0-9]*\)", traceLog) == None:
        return TraceElement(-1, -1, "wrong", "wrong")
          
    pid = re.search("\([\s0-9]*\)", traceLog)
    if pid:
        if PARSE_DBG:
            print pid.group(0)
        pid = int(pid.group(0)[1:-1])
        
    
    ts = re.search("\s[0-9]*.[0-9]*:", traceLog)
    if ts:
        if PARSE_DBG:
            print ts.group(0)
        ts = int(float(ts.group(0)[1:-1]) * 1000)

    flag = ""
    tagName = ""
    traceLogContent = re.search(r"tracing_mark_write:\s*\S(\|[0-9]*\|\S*){0,1}", traceLog)
    if traceLogContent:
        if PARSE_DBG:
            print traceLogContent.group(0)
        traceLogContent = traceLogContent.group(0).strip().split(":")[1].split("|")
        if len(traceLogContent) == 1:
            flag = traceLogContent[0].strip()
            tagName = ""
        else:
            flag = traceLogContent[0].strip()
            tagName = traceLogContent[2].strip()

    return TraceElement(ts, pid, flag, tagName)
