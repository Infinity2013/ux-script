#!/usr/bin/env python
import subprocess
import os
import sys
import platform
import re

def getArgs():
    args = {}
    layer = raw_input("Layer: ")
    packageName = raw_input("PackageName: ")
    uiobject_name = raw_input("UiobjectName: ")
    sleep_time = raw_input("SleepTime: ")
    outName = "\"%s-%s_%s.launch\" %s (\"%s\", ic.board(), ic.release())" % ("%s", "%s", "%s", "%", re.sub("\s", "_", uiobject_name))
    args["layer"] = layer
    args["packageName"] = packageName
    args["outName"] = outName
    args["uiobject_name"] = uiobject_name
    uiobject_name = re.sub(r"\s+", "_", uiobject_name)
    args["sleep_time"] = sleep_time
    args["repeat"] = 5
    return args

def writeHeader(outfd):
    path = "%s/%s" % (sys.path[0], "header")
    fd = open(path, "r")
    content = fd.readlines()
    for line in content:
        outfd.write(line)

def writeArgs(outfd, args):
    outfd.write("args = {}\n")
    for key in args.keys():
        if key in ("repeat", "sleep_time"):
            continue
        elif key == "outName":
            line = "args[\"%s\"] = %s\n" % (key, str(args.get(key)))
        else:
            line = "args[\"%s\"] = \"%s\"\n" % (key, str(args.get(key)))
        outfd.write(line)
    outfd.write("args[\"repeat\"] = a[0].repeat\n")
    outfd.write("args[\"sleep_time\"] = a[0].slee_time\n")
    outfd.write("args[\"systrace\"] = a[0].systrace\n")
    outfd.write("doQALaunchTime(args)")

def writeEnding(outfd, args):
    line = "p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author wxl')\n"
    outfd.write(line)
    line = "p.add_argument('-t', default=%s,  dest='slee_time', type=int, help='sleep_time')\n" % (args.get("sleep_time"))
    outfd.write(line)
    line = "p.add_argument('-r', default=%d,  dest='repeat', type=int, help='repeat')\n" % (args.get("repeat"))
    outfd.write(line)
    line = "p.add_argument('--systrace', default='', dest='systrace', nargs='+', help='systrace tags')\n"
    outfd.write(line)
    outfd.write("a = p.parse_known_args(sys.argv)\n")


def main():
    if platform.system() != "Linux":
        return
    args = getArgs()
    fn_script = "%s_launch.py" % (re.sub("\s", "_", args.get("uiobject_name")))
    fn_path = "%s/%s" % (sys.path[0], fn_script)
    fd = open(fn_path, "w")
    writeHeader(fd)
    fd.write("\n")
    writeEnding(fd, args)
    fd.write("\n")
    writeArgs(fd, args)
    fd.close()
    cmd = "chmod +x %s " % fn_path
    os.system(cmd)


if __name__ == '__main__':
    main()
