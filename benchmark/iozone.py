#!/usr/bin/env python
from adb import adb
import time
import os
import sys
import re


def prepare():
    adb.cmd("shell '/data/iozone -ec -+n -L64 -S32 -s50M -f /data/iozone.tmp -r512k -i0 -w > /dev/null'").communicate()

def random_rw():
    # random read
    lines = adb.cmd("shell '/data/iozone -ec -+n -L64 -S32 -s50M -f /data/iozone.tmp -w -+N -I -r4k -i2 -O'").communicate()[0].splitlines()
    for i in xrange(len(lines)):
        if "KB  reclen   write rewrite    read    reread    read   write    read  rewrite     read   fwrite frewrite   fread  freread" in lines[i]:
            t = lines[i + 1]
            t = t.split()
            rw = float(t[2])
            rr = float(t[3])
            return rw, rr
    else:
        raise ValueError("No result found in random_rw.")

def sequential_write():
    lines = adb.cmd("shell '/data/iozone -ec -+n -L64 -S32 -s50M -f /data/iozone.tmp -w -+N -I -r512k -i0'").communicate()[0].splitlines()
    for i in xrange(len(lines)):
        if "KB  reclen   write rewrite    read    reread    read   write    read  rewrite     read   fwrite frewrite   fread  freread" in lines[i]:
            t = lines[i + 1]
            t = t.split()
            sw = float(t[2]) / 1024
            return sw
    else:
        raise ValueError("No result found in sequential_write.")


def sequential_read():
    lines = adb.cmd("shell '/data/iozone -ec -+n -L64 -S32 -s50M -f /data/iozone.tmp -w -+N -I -r512k -i1'").communicate()[0].splitlines()
    for i in xrange(len(lines)):
        if "KB  reclen   write rewrite    read    reread    read   write    read  rewrite     read   fwrite frewrite   fread  freread" in lines[i]:
            t = lines[i + 1]
            t = t.split()
            sr = float(t[2]) / 1024
            return sr
    else:
        raise ValueError("No result found in sequential_read.")

def drop_cache():
    adb.cmd("shell 'sync && echo 3 > /proc/sys/vm/drop_caches'").communicate()

def main():
    prepare()
    index = 0
    repeat = 5
    res_dict = {}
    for item in ['rw', 'rr', 'sw', 'sr']:
        res_dict[item] = []
    print "random_write  random_read  sequential_write  sequential_read"
    while index < repeat:
        drop_cache()
        rw, rr = random_rw()
        drop_cache()
        sw = sequential_write()
        drop_cache()
        sr = sequential_read()
        print "%10.3f  %9.3f  %15.3f  %14.3f" % (rw, rr, sw, sr)
        res_dict['rw'].append(rw)
        res_dict['rr'].append(rr)
        res_dict['sw'].append(sw)
        res_dict['sr'].append(sr)
        index += 1
        time.sleep(60)

    for k in res_dict:
        res_dict[k].sort()

    for k in res_dict:
        print "%s: %f" % (k, res_dict[k][(len(res_dict[k]) / 2)])

if __name__ == '__main__':
    main()
