#!/usr/bin/env python
import subprocess
import os
import sys
import time

def parseInfo(info):
    line = info.strip().split()
    dic = {}
    dic["id"] = int(line[0][-1])
    dic["user"] = int(line[1])
    dic["nice"] = int(line[2])
    dic["sys"] = int(line[3])
    dic["idle"] = int(line[4])
    dic["iowait"] = int(line[5])
    dic["irq"] = int(line[6])
    dic["softirq"] = int(line[7])
    return dic

def getInfo():
    cmd = "adb shell \"cat /proc/stat\""
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    content = p.stdout.readlines()
    '''
    cpu0 5488 254 6426 193130 1715 0 156 0 0 0
    '''
    dicList = []
    for i in xrange(1, 5):
        dicList.append(parseInfo(content[i]))
    return dicList

def cpu_utilization(prev, cur):
    resDic = {}
    curTotal = 0
    for key in prev.keys():
        if key == "id":
            resDic[key] = prev.get(key)
            continue
        resDic[key] = cur.get(key) - prev.get(key)
        curTotal += resDic.get(key)
    print "cpu%d: %4d %4d %3d %4d %6d %3d %7d" % (resDic.get("id"), resDic.get("user") * 100 / curTotal, resDic.get("nice") * 100 / curTotal, resDic.get("sys") * 100 /curTotal, resDic.get("idle") * 100 / curTotal, resDic.get("iowait") * 100 / curTotal, resDic.get("irq") * 100 / curTotal, resDic.get("softirq") * 100 / curTotal)


def main():
    curList = getInfo()
    while True:
        prevList = curList
        time.sleep(0.5)
        curList = getInfo()
        print ("cpunu user nice sys idle iowait irq softirq")
        for i in xrange(0, len(prevList)):
            cpu_utilization(prevList[i], curList[i])
        print "--------------------------------------"

if __name__ == "__main__":
    main()
