#!/usr/bin/env python
import subprocess
import os
import sys
import adbhelper

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


        

def main():
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
