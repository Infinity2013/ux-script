#!/usr/bin/env python
'''
Created on Aug 8, 2014

@author: wxl
'''
from argparse import ArgumentParser
import os
import re
import subprocess
import sys
import threading
import time
'''
Global Config
'''
DBG = False
ADB_COMMAND = "adb shell getevent -t"
SQUARE_OF_MARGIN_OF_COORDINATE = 200 * 200

    
class Coordinate():
    type = ""
    firstCoordinates = []
    lastCoordinates = []
    duration = 0
    def __init__(self, type, firstCoordinates, lastCoordinates, duration):
        self.type = type
        self.firstCoordinates = firstCoordinates
        self.lastCoordinates = lastCoordinates
        self.duration = duration
        if DBG:
            print ("Coordinate:\n")
            print ("type: %s\n") % (self.type)
            print ("first: %d, %d\n") % (self.firstCoordinates[0], self.firstCoordinates[1])
            print ("last: %d, %d\n") % (self.lastCoordinates[0], self.lastCoordinates[1])
            print ("duartion: %d\n") % (self.duration)

    def dumpToFile(self, file):        
        file.write("type:" + self.type + "\n")
        file.write("firstCoordinate:" + str(self.firstCoordinates[0]) + " " + str(self.firstCoordinates[1]) + "\n")
        file.write("lastCoordinates:" + str(self.lastCoordinates[0]) + " " + str((self.lastCoordinates[1])) + "\n")
        file.write("duration:" + str(self.duration) + "\n")

    def sendToDevice(self):
        time.sleep(0.01)
        if (self.type == "tap"):
            cmd = ("adb shell input tap %d %d") % (self.firstCoordinates[0], self.firstCoordinates[1])
            if DBG:
                print cmd
            os.system(cmd)
        elif self.type == "swipe":
            cmd = ("adb shell input swipe %d %d %d %d %d") % (self.firstCoordinates[0], self.firstCoordinates[1], self.lastCoordinates[0], self.lastCoordinates[1], self.duration)
            if DBG:
                print cmd
            os.system(cmd)        
        
class CollectInputEventThread(threading.Thread):
    finish = False
    eventList = []
    def run(self):
        p = subprocess.Popen(ADB_COMMAND, shell = True, stdout = subprocess.PIPE)
        while self.finish != True:
            event = p.stdout.readline()
            if DBG:
                print event
            self.eventList.append(event)

    def stop(self):
        self.finish = True

    def getEventList(self):
        return self.eventList

'''
[1407464502.856670] /dev/input/event0: 0003 0039 0000019e  begin 
[1407464502.856670] /dev/input/event0: 0003 0035 00000177  x
[1407464502.856670] /dev/input/event0: 0003 0036 0000043b  y
[1407464502.856670] /dev/input/event0: 0003 003a 00000022  unknow
[1407464502.856670] /dev/input/event0: 0000 0000 00000000  sync 
[1407464502.920761] /dev/input/event0: 0003 0039 ffffffff  end
[1407464502.920761] /dev/input/event0: 0000 0000 00000000  sync
'''
def divideEventList2Movement(eventList):
    movementIndexList = []
    for i in range(len(eventList)):
        if re.findall("0003\s0039", eventList[i]) != []:
            movementIndexList.append(i)

    if len(movementIndexList) % 2 != 0:
        print ("There are sth wrong in eventList, divideEventList2Movement failed")

    if DBG:
        print movementIndexList
    return movementIndexList

def square_diff(list1, list2):
    res = list2[0] * list2[0] + list2[1] * list2[1] - list1[0] * list1[0] - list1[1] * list1[1]
    res = abs(res)
    if DBG:
        print ("squaure dif: %d\n") % (res)
    return res
'''
Input:
[1407464502.856670] /dev/input/event0: 0003 0035 00000177
          ........
Output:
2856 unit:ms
'''
def getTimeStamp(event):
    fractionPart = 0
    integerPart = 0
    '''
    [1407464502.856670]
    [1407464502.856670
    '''
    ts = event.split("]")[0][1:]
    ts = ts.split(".")

    '''
    integerPart:1407464502
    fractionPart: 856670
    '''
    integerPart = int(ts[0].strip("\s"))
    fractionPart = int(ts[1].strip("\s"))
    '''
    intergerPart:2
    fractionPart: 856
    '''
    integerPart %= 10
    fractionPart /= 1000
    '''
    ts = 2856
    '''
    ts = integerPart * 1000 + fractionPart

    return ts    
    
'''
Coordinates:
[1407464502.856670] /dev/input/event0: 0003 0035 00000177  x
[1407464502.856670] /dev/input/event0: 0003 0036 0000043b  y
Types:
Only support 2 types at present:tap, swipe
tap: tap on one point to click on something
swip: move from one position to another to finish a flip movement
'''
def extractCoordinatesAndTypeFromMovement(eventList, startIndex, endIndex):

    if DBG:
        print ("extractCoordinatesAndTypeFromMovement(%d, %d)") % (startIndex, endIndex)
        print ("start: %s") % eventList[startIndex]
        print ("end: %s") % (eventList[endIndex])
    coordinateDic = {}
    index = 0
    '''
    Coornidates usually appears in pairs, but sometime they dismiss one of them.
    So we only consider the coordinates that appear in pairs.
    '''
    for i in range(startIndex, endIndex):
        if re.findall("0003\s0035", eventList[i]) != []:
            if re.findall("0003\s0036", eventList[i + 1]) != []:
                index += 1
                '''
                [1407464502.856670] /dev/input/event0: 0003 0035 00000177
                0                   1                  2    3    4
                or
                [  28888888.j44444] /dev/input/event0: 0003 0025 00000177
                0  1                2                  3    4    5                
                '''                          
                xCoordinate = int(eventList[i].split()[-1], 16)
                yCoordinate = int(eventList[i + 1].split()[-1], 16)
                if DBG:
                   print ("x: %d, y: %d\n") % (xCoordinate, yCoordinate)

                coordinateDic[index] = [xCoordinate, yCoordinate]

    if coordinateDic == {}:
        return None
    
    firstCoordinates = coordinateDic[1]
    lastCoordinates = coordinateDic[index]

    type = ""

    if square_diff(firstCoordinates, lastCoordinates) < SQUARE_OF_MARGIN_OF_COORDINATE:
        type = "tap"
    else:
        type = "swipe"

    firstTs = getTimeStamp(eventList[startIndex])
    lastTs = getTimeStamp(eventList[endIndex])
    duration = lastTs - firstTs
    if DBG:
       print ("duration: " + str(duration) + "\n")

    coordinate = Coordinate(type, firstCoordinates, lastCoordinates, duration)

    return coordinate

def main():
    global DBG
    p = ArgumentParser(usage='getevent.py -d -o file', description='Author wxl')
    p.add_argument('-d', default=0,  dest='debug', action="store_true", help='enable debug info')
    p.add_argument('-o', dest="output", default="wxl.event", help="output filename")
    args = p.parse_known_args(sys.argv)

    DBG = args[0].debug
    output = args[0].output

    thread = CollectInputEventThread()
    thread.setDaemon(True)

    cmd = raw_input("Press any key to start")
    thread.start()
    cmd = raw_input("Press any key to stop")
    if DBG:
        print ("Dumping eventList...\n")
    thread.stop()
    eventList = thread.getEventList()
    if DBG:
        print eventList
        
    if DBG:
        print ("Processing...\n")
    fd = open(output, "w")
    movementIndexList = divideEventList2Movement(eventList)

    for i in range(0, len(movementIndexList), 2):
        coordinate = extractCoordinatesAndTypeFromMovement(eventList, movementIndexList[i], movementIndexList[i + 1])
        if coordinate != None:
            coordinate.dumpToFile(fd)   

    fd.flush()
    fd.close()
    if DBG:
        print ("Done!\n")
    
if __name__ == "__main__":
    main()


    
                

                
        
    
