#!/usr/bin/env python
import zipfile
import sys

X86 = 0
ARMV7 = 1
ARM = 2


def libinfo(name):
    x86List = []
    armv7List = []
    armList = []
    apk = zipfile.ZipFile(name)
    nameList = apk.namelist()

    for name in nameList:
        if "x86" in name:
            x86List.append(name)
        elif "armeabi-v7a" in name:
            armv7List.append(name)
        elif "armeabi" in name:
            armList.append(name)
    return [x86List, armv7List, armList]


def report(libList):
    x86 = len(libList[X86])
    armv7 = len(libList[ARMV7])
    arm = len(libList[ARM])

    competitor = max(armv7, arm)

    type = ""
    diff = 0
    if x86 != 0:
        type = "x86"
        diff = x86 - competitor
    elif competitor == 0:
        type = "Java"
    else:
        type = "arm"
    return [type, diff]


def main():
    name = sys.argv[1]
    libList = libinfo(name)
    info = report(libList)
    output = "%-50s %s %s" % (name, info[0], info[1])
    print output
if __name__ == "__main__":
    main()
