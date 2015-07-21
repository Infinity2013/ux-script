#!/usr/bin/env python
from uiautomator import device as d
from adb import adb
from clog import colorlog as cl
import xml.etree.cElementTree as ET
import time
from argparse import ArgumentParser
import sys
import re

def parse(name):
    score = 0
    tree = ET.parse(name)
    root = tree.getroot()
    for child in root[0]:
        if child.tag == "fps":
            score = float(child.text.strip("fps"))
            break
    return score

def getlastRes():
    '''
    resList = {}
    cacheList = adb.cmd('shell "ls /sdcard/Android/data/com.glbenchmark.glbenchmark27/cache"').stdout.readlines()
    for f in cacheList:
        r = re.match(r'results_.+_(?P<index>\d+).xml', f)
        if r is not None:
            resList[r.group("index")] = f.strip()
    keyList = resList.keys()
    keyList.sort()
    last = resList.get(keyList[-1])
    '''
    adb.cmd("pull /sdcard/Android/data/com.glbenchmark.glbenchmark27/cache/last_results_2.7.0.xml ./last_results_2.7.0.xml").communicate()

def check(text):
    view = d(text=text)
    view.click()

def startapp():
    adb.cmd("shell am start com.glbenchmark.glbenchmark27/com.glbenchmark.activities.GLBenchmarkDownloaderActivity")
    time.sleep(2)

def terminateapp():
    adb.cmd("shell am force-stop com.glbenchmark.glbenchmark27")
    time.sleep(2)

def performancetest():
    d(text="Performance Tests").click()
    time.sleep(2)

def clearchoice():
    d(text="All").click()
    time.sleep(1)
    d(text="None").click()
    time.sleep(1)


def doCase(case, duration, repeat, fling=False):
    resList = []
    index = 0
    while(index < repeat):
        startapp()
        performancetest()
        clearchoice()
        if fling:
            d(scrollable=True).fling.toEnd()
        check(case)
        d(text="Start").click()
        time.sleep(duration)
        getlastRes()
        res = parse("last_results_2.7.0.xml")
        print res
        resList.append(res)
        terminateapp()
        index += 1
    resList.sort()
    return resList

def main():
    p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author wxl')
    p.add_argument('-r', default=10,  dest='repeat', type=int, help='repeat')
    a = p.parse_known_args(sys.argv)
    print doCase("C24Z16 Offscreen ETC1", 90, a[0].repeat)
    print doCase("C24Z16 Offscreen Auto", 150, a[0].repeat, True)

if __name__ == "__main__":
    main()
