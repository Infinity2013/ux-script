#!/usr/bin/env python
import os
import sys
import re
import subprocess
import adbhelper
from clog import colorlog as colog
from argparse import ArgumentParser

def main():
    p = ArgumentParser(usage='sendevent.py -d -f file', description='Author wxl')
    p.add_argument('-d', default=0,  dest='debug', action="store_true", help='enable debug info')
    p.add_argument('-p', dest="pstate", help="set pstate instead of freq", default=0)
    args = p.parse_known_args(sys.argv)
    
    debug = args[0].debug
    pstate = args[0].pstate
    
    if debug == 1:
        colog.setLevel("v|e|c|w|d")

    if pstate != 0:
        set_pstate(pstate)
    else:
        freq()
    

def set_pstate(pstate):
    cmd = "adb shell \"echo %s > /sys/devices/system/cpu/intel_pstate/max_perf_pct\"" % pstate
    os.system(cmd)

def getFreq():
    pattern = "adb shell cat /sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq"
    for i in xrange(4):
        cmd = pattern % (i)
        print "Cpu %d:" % i
        os.system(cmd)

def setFreq(freq):
    print "setFreq start!"
    pattern = "adb shell \"echo %d > /sys/devices/system/cpu/cpu%d/cpufreq/scaling_max_freq\""
    for i in xrange(4):
        cmd = pattern % (freq, i)
        os.system(cmd)
    print "setFreq done!"
    getFreq()

def getFreqList():
    cmd = "adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies"
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    content = p.stdout.readline()
    if content == None or content == "":
        print "No this sysfs!"
        sys.exit()
    content = content.strip().split()
    return content


        

def freq():
    freqList = getFreqList()
    index = 1
    for freq in freqList:
        print "%d: %s" % (index, freq) 
        index += 1
    cmd = int(raw_input("which one?" ))
    adbhelper.root()
    getFreq()
    setFreq(int(freqList[cmd - 1]))

if __name__ == "__main__":
    main()
