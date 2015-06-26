#!/usr/bin/env python

import re
import os
import sys
import subprocess
import time

PARSE_DBG = False

class StraceElement():

    def __init__(self, ts, callname, fd, ret):
        self.ts = ts
        self.callname = callname
        self.fd = fd
        self.ret = ret

    def dump(self):
        print "%f %s(%s) = %s" % (self.ts, self.callname, self.fd, self.ret)

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
        print ("[%f] %s") % (self.ts, self.content)

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
    elif type == "strace":
        return parse2StraceElement(log)
    else:
        print "Error: unsupported type %s" % type
        sys.exit()
'''
pattern:
01-02 17:58:35.603  1982  2395 W SurfaceFlinger: Timed out waiting for hw vsync; faking it
'''
def parse2LogcatElement(logcatLog):
    r = re.match(r"\d+\-\d+\s(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\.(?P<milli>\d{3})\s+(?P<pid>\d+)\s+(?P<tid>\d+)\s+(?P<type>\S)\s+(?P<tag>\S+):\s+(?P<content>.*$)", logcatLog)
    if r is None:
        return LogcatElement(0, 0, 0, "", "", "")
    ts = (int(r.group("hour")) * 3600 + int(r.group("minute")) * 60 + int(r.group("second"))) * 1000 + int(r.group("milli"))
    return LogcatElement(ts, int(r.group("pid")), int(r.group("tid")), r.group("type"), r.group("tag"), r.group("content"))


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
    if re.search("\S*-[0-9]*\s*\([\s0-9]*\)", traceLog) is None:
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

def parse2StraceElement(strace):
    strace = strace.strip()
    strace = strace.split("=")
    ret = int(strace[-1])
    leftcurve = strace[0].index("(")
    firstcomma = strace[0].index(",")
    fd = strace[0][leftcurve + 1: firstcomma]
    firstspace = strace[0].index(" ")
    callname = ""
    ts = 0
    if firstspace > leftcurve:
        '''means no ts'''
        callname = strace[0][:leftcurve]
        ts = 0
    else:
        callname = strace[0][firstspace + 1:leftcurve]
        ts = float(strace[0][:firstspace]) * 1000

    return StraceElement(ts, callname, fd, ret)
