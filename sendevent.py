#!/usr/bin/env python
'''
Created on Aug 8, 2014

@author: wxl
'''
from argparse import ArgumentParser
from clog import clog
from getevent import Coordinate
import re
import sys
'''
global Config
'''
DBG = False

def generateCoordinate(coordinateList, index):
    if DBG:
        for i in range(index, index + 4):
            print coordinateList[i]    
    type = coordinateList[index].split(":")[1].strip()
    firstCoordinate = coordinateList[index + 1].split(":")[1].strip()
    firstCoordinate = [int(firstCoordinate.split()[0]), int(firstCoordinate.split()[1])]
    lastCoordinate = coordinateList[index + 2].split(":")[1].strip()
    lastCoordinate = [int(lastCoordinate.split()[0]), int(lastCoordinate.split()[1])]
    duration = int(coordinateList[index + 3].split(":")[1].strip())

    coordinate = Coordinate(type, firstCoordinate, lastCoordinate, duration)
    return coordinate
    
def main():
    global DBG
    p = ArgumentParser(usage='sendevent.py -d -o file', description='Author wxl')
    p.add_argument('-d', default=0,  dest='debug', action="store_true", help='enable debug info')
    p.add_argument('-f', dest="input", help="intput filename", required=True)
    args = p.parse_known_args(sys.argv)

    DBG = args[0].debug
    inputfile = args[0].input
    sendEvent(inputfile)

def sendEvent(inputfile):
    coordinateIndexList = []
    
    fd = open(inputfile, "r")
    coordinateList = fd.readlines()
    for i in range(len(coordinateList)):
        if re.findall("type:", coordinateList[i]) != []:
            coordinateIndexList.append(i)

    for item in coordinateIndexList:
        coordinate = generateCoordinate(coordinateList, item)
        coordinate.sendToDevice()

    fd.close()

if __name__ == "__main__":
    main()
