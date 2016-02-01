#!/usr/bin/env python
import os
import re
import subprocess
import sys
import zipfile

X86 = 0
ARMV7 = 1
ARM = 2


def libinfo(name):
    lib_dict = {}
    lib_dict['x86'] = []
    lib_dict['armv7'] = []
    lib_dict['arm'] = []
    apk = zipfile.ZipFile(name)
    nameList = apk.namelist()

    for name in nameList:
        if "x86" in name:
            lib_dict['x86'].append(name)
        elif "armeabi-v7a" in name:
            lib_dict['armv7'].append(name)
        elif "armeabi" in name:
            lib_dict['arm'].append(name)
    return lib_dict


def report(lib_dict):
    x86 = len(lib_dict['x86'])
    armv7 = len(lib_dict['armv7'])
    arm = len(lib_dict['arm'])

    competitor = max(armv7, arm)

    if x86 >= competitor:
        type = "x86"
    elif competitor == 0:
        type = "Java"
    else:
        type = "arm"
    return type


def package_info(name):
    file_path = "%s/%s" % (os.getcwd(), name)
    file_path = file_path.replace(" ", "\ ")
    cmd = "aapt d badging %s" % file_path
    dump_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].splitlines()
    p_info = {}
    for line in dump_info:
        if "application-label:" in line:
            g = re.match(r"application-label:'(?P<label>.*)'.*", line)
            p_info['label'] = g.group('label')
        elif "versionName" in line:
            g = re.match(r"package:\s+name='(?P<package>[\w\.]+)'\s+versionCode='(?P<vcode>\d+)'\s+versionName='(?P<vname>[\w\.]+)'.*", line)
            p_info['package'] = g.group('package')
            p_info['vcode'] = g.group('vcode')
            p_info['vname'] = g.group('vname')
    if p_info == {}:
        print "Failed to get package info"
    return p_info


def main():
    name = sys.argv[1]
    lib_dict = libinfo(name)
    info = report(lib_dict)
    p_info = package_info(name)
    if p_info != {}:
        if name != "%s.apk" % p_info['package']:
            os.rename(name, "%s.apk" % p_info['package'])
        print "%-40s%-10s%-5s%-40s" % (p_info['package'], p_info['vname'], info, p_info['label'])
if __name__ == "__main__":
    main()
