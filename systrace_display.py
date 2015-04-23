#!/usr/bin/env python

import loghelper
import adbhelper
import os
import re

last_head_ts = 0
last_tail_ts = 0
tags = "gfx wm am input view power"
def start_tracing(tags):
    cmd = "adb shell \"atrace --async_start %s\"" % (tags)
    os.system(cmd)

def stop_tracing(out):
    cmd = "adb shell \"atrace --async_dump -z\" > out.trace"
    os.system(cmd)
    cmd = "systrace.py --from-file=out.trace -o %s" % out
    os.system(cmd)

def dump_dmseg(out):
    cmd = "adb shell dmesg > %s" % out
    os.system(cmd)

def merge_dmesg_to_systrace(dmesg, systrace, out):
    dmesg_fp = open(dmesg, "r")
    systrace_fp = open(systrace, "r")
    
    #step 1 find the head and tail
    dmesg_content = dmesg_fp.readlines()
    head = 0
    tail = 0
    for dmesg in dmesg_content:
        element = loghelper.parse2Element(dmesg, "dmesg")
        if "resume from mwait" in element.content:
            head = element
        elif "Restarting tasks" in element.content:
            tail = element
    dmesg_fp.close()

    #stpe 2 read systrace log
    systrace_content = systrace_fp.readlines()
    systrace_fp.close()
    

    #step 3 based on ts, add head and tail to right position of systrace log
    head_systrace = "%s-%d ( %d) [000] ...1 %f: tracing_mark_write: B|%d|kernelWakeUp\\n\\\n" % ("dmesg", 22, 22, float(float(head.ts) / 1000), 22)
    tail_systrace = "%s-%d ( %d) [000] ...1 %f: tracing_mark_write: E|%d|kernelWakeUp\\n\\\n" % ("dmesg", 22, 22, float(float(tail.ts) / 1000), 22)
    
    systrace_content.insert(-5, head_systrace)
    systrace_content.insert(-5, tail_systrace)
    out_content = ("").join(systrace_content)
    out_fp = open(out, "w")
    out_fp.write(out_content)
    out_fp.flush()
    out_fp.close()

def systrace_endpoint(systrace):
    systrace_fd = open(systrace, "r")
    systrace_content = systrace_fd.readlines()
    surfaceflinger_list = []
    brightness_list = []
    for trace in systrace_content:
        if "surfaceflinger" in trace:
            surfaceflinger_list.append(loghelper.parse2Element(trace, "trace"))
        if "setBrightness" in trace:
            brightness_list.append(loghelper.parse2Element(trace, "trace"))
    #the longest setBrightness should be the first two trace in brightness list
    first_setBrightness_ts = brightness_list[1].ts - brightness_list[0].ts

    endflag_list = []
    for trace in surfaceflinger_list:
        if trace.flag == "E":
            endflag_list.append(trace.ts)

    endflag_list.sort()
    
    endpoint = 0
    for ts in endflag_list:
        if ts > first_setBrightness_ts:
            endpoint = ts
            break

    return endpoint 

def dmesg_startpoint(dmesg):
    global last_head_ts, last_tail_ts
    dmesg_fp = open(dmesg, "r")
    dmesg_content = dmesg_fp.readlines()
    head = 0
    tail = 0
    for dmesg in dmesg_content:
        element = loghelper.parse2Element(dmesg, "dmesg")
        if "resume from mwait" in element.content:
            head = element
        elif "Restarting tasks" in element.content:
            tail = element
    dmesg_fp.close()

    if head == 0 or tail == 0:
        return [0, 0]
    if head.ts == last_head_ts or tail.ts == last_tail_ts:
        return [0, 0]
    else:
        last_head_ts = head.ts
        last_tail_ts = tail.ts
    return [head.ts, tail.ts - head.ts]



def main():
    dir_name = raw_input("Please enter a name: ")
    pwd = os.getcwd()
    cur_path = "%s/%s" % (pwd, dir_name)
    if os.path.exists(cur_path):
        cmd = "rm -rf %s" % cur_path
        os.system(cmd)
    os.makedirs(cur_path)
    os.chdir(cur_path)

    output_list = []
    index = 0

    res_list = []

    releaseInfo = adbhelper.getDeviceInfo()
    resOutput = "%s(%s).res" % (dir_name, releaseInfo)
    out_fd = open(resOutput, "w")

    start_tracing(tags)

    cmd = raw_input("Enter any key to start.")
    while cmd != "f":
        index += 1
        outputpreffix = "%s_%d\(%s\)" % (dir_name, index, releaseInfo)
        dmesg_output = "%s.dmesg" % outputpreffix
        systrace_output = "%s.html" % outputpreffix

        stop_tracing(systrace_output)
        dump_dmseg(dmesg_output)

        dmesg_output = re.sub("\\\\", "", dmesg_output)
        systrace_output = re.sub("\\\\", "", systrace_output)

        print "%s %s" % (dmesg_output, systrace_output)
        
        startpoint = dmesg_startpoint(dmesg_output)
        endpoint = systrace_endpoint(systrace_output)

        res = endpoint - startpoint[0]
        if startpoint > 0 and startpoint < 1:
            res_list.append(res)
        content = "index %d: %d - %d = %d\n" % (index, res, startpoint[1], res - startpoint[1]);
        print content
        out_fd.write(content)
        start_tracing(tags)
        cmd = raw_input("Press any key to continue or f to stop.")

    res_list.sort()
    content = "middle var: %d\n" % (res_list[len(res_list) / 2]);
    out_fd.write(content)


if __name__ == "__main__":
    main()








