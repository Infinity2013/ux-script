import os
import re
import time

import matplotlib as pl
from matplotlib.ticker import MultipleLocator, FuncFormatter
import numpy as np

def showGraph():
    global outputDir
    global resultFile

    MultipleLocator.MAXTICKS = 100000
    fig = pl.figure(figsize=(10,6))

    x = np.arange(0, 77, 1)
    y = []
    z = []
    t = []



def checkDeviceExist():
    '''
    List of devices attached
    3d796acc	device
    '''
    print "==check if device is connected=="
    ret = os.popen("adb devices")
    result = ret.read()
    index = result.find("device");
    index2 = result.find("device", index+1)
    if index2 == -1:
        print "please connect your device"
        exit()

def getLogs():
    global outputDir
    #checkDeviceExist()

    currentTime = time.strftime('%Y-%m-%d_%H:%M:%S')
    outputDir = logDir+currentTime+"/"
    if os.path.exists(outputDir) == False:
        os.makedirs(outputDir)

    dmesgCommand = "adb shell dmesg > " + outputDir + dmesgFile
    bootProgressCommand = "adb logcat -b all -v time -d | grep -E 'boot_progress|bootanim|BootAnimation' > " + outputDir + bootProgressFile
    print "==Get dmesg log=="
    os.system(dmesgCommand)
    print "==Get boot progress events log=="
    os.system(bootProgressCommand)

def parseLogs():
    global outputDir
    global dmesgFile
    global bootProgressFile
    # parse dmesg
    print "==parse dmesg log=="
    # dmesgkeyString is used from linux/scripts/bootgraph.pl, it can be used as the timenode for kernel startup end  and init start
    # dmesgKeyString = "Write protecting the"
    dmesgKeyString = "Freeing unused kernel memory"
    dmesgLogFileName = outputDir + dmesgFile
    print "dmesglogfile is " + dmesgLogFileName
    dmesg_log = open(dmesgLogFileName)
    line = dmesg_log.readline()
    while line:
        line = line.strip()
        index = line.find(dmesgKeyString)
        if index != -1:
            break
        line = dmesg_log.readline()
    print line
    # <6>[    4.123123] Freeing unused kernel memory: 852K (ffffffff820c9000 - ffffffff8219e000)
    dmesgKey = "start_init"
    tempTimeNode = line[line.find("[") :line.find("]")].split(" ")[-1]
    print tempTimeNode
    timeNode = int(float(tempTimeNode)*1000)
    resultDict[dmesgKey] = timeNode
    resultList.append(dmesgKey)
    resultList.append(timeNode)


    # parse boot_progress
    print "==parse boot progress events log=="
    bootLogFileName = outputDir + bootProgressFile
    boot_progress = open(bootLogFileName)
    logs = boot_progress.readlines()
    refer_ts = 0
    refer_duration = 0
    for i in xrange(len(logs)):
	log = logs[i]
        g = re.match(r'.*\d{2}:(?P<minute>\d{2}):(?P<sec>\d{2})\.(?P<msec>\d{3}).*I\/(?P<content>.*)', log)
        if g is not None:
            bootKey = ''
            bootTs = ''
	    if 'boot_progress' in log:
		refer_ts = getTime(g)
		g = re.match(r'(?P<key>boot_progress_\w+)\(.*:\s+(?P<duration>\d+).*', g.group('content'))
		bootKey = g.group('key')
		bootTs = g.group('duration')
		refer_duration = int(bootTs)
            elif 'Starting service' in log:
                bootKey = 'bootanim start'
                bootTs = getTime(g)
            elif 'exited with status' in log:
                bootKey = 'bootanim exit'
                bootTs = getTime(g) - refer_ts + refer_duration
            elif 'BootAnimation' in log:
                bootKey = 'BootAnimation'
                bootTs = getTime(g) - refer_ts + refer_duration
            else:
                continue
	    if bootKey != '' and bootTs != '':
	        resultDict[bootKey] = bootTs
                resultList.append(bootKey)
                resultList.append(bootTs)
    if 'bootanim start' in resultDict:
        resultDict['bootanim start'] = resultDict['bootanim start'] - refer_ts + refer_duration
	resultList[resultList.index('bootanim start') + 1] = resultDict['bootanim start']

'''
    line = boot_progress.readline()
    while line:
        #'I/boot_progress_start( 2758): 10124\r\n'
        # 01-03 23:56:20.309 I/boot_progress_start( 2227): 6895
        line = line.strip()
        line = line.split(" ")
        timeNode = line[-1]
        bootKey = ""
        for i in line:
            if i.find("boot_pro") != -1:
                bootKey = i.split("/")[1].split("(")[0]
        bootKey = bootKey[14:]
        #print bootKey
        #print timeNode
        resultDict[bootKey] = timeNode
        resultList.append(bootKey)
        resultList.append(timeNode)
        #print resultDict
        line = boot_progress.readline()
'''

def getTime(g):
    return int(g.group('minute')) * 60 * 1000 + int(g.group('sec')) * 1000 + int(g.group('msec'))


def showResult():
    global outputDir
    #for i in resultDict:
    #    print "resultDict[%s] = " %i, resultDict[i]
    #print sorted(resultDict.iteritems(), key=lambda d:d[1], reverse = False)
    i = 0

    resultKey = []
    resultTimeNode = []
    for j in range(len(resultList)):
        if j%2 == 0:
            resultKey.append(resultList[j])
        else :
            resultList[j] = str(float(resultList[j])/1000)
            resultTimeNode.append(resultList[j])

    print "\n\nResult ================================"
    for j in resultKey:
        print j
    for j in resultTimeNode:
        print j


    print "\n\nResult ================================"
    out = open(outputDir+resultFile,'w')
    for j in range(len(resultList)/2):
        out.write(str(resultList[j*2]) + " " + str(resultList[j*2+1]) + "\n")
        print str(resultList[j*2]) + " " + str(resultList[j*2+1])
    out.close()

'''
    produces for cold boot time info analysis:
    getLogs: dmesg and boot events
    parse the logs and generate the useful result
    output
'''
def main():
    print "main"
    if os.path.exists(logDir) == False:
        os.makedirs(logDir)
    getLogs()
    parseLogs()
    showResult()

logDir="logs/"
outputDir = ""
dmesgFile = "dmesg.log"
bootProgressFile = "boot_progress.log"
resultFile = "out.result"
resultDict = {}
resultList = []
if __name__ == '__main__':
    main()

