#!/usr/bin/env python
import os
import platform
import re
import sys
from argparse import ArgumentParser


def getArgs():
    args = {}
    layer = raw_input("Layer: ")
    packageName = raw_input("PackageName: ")
    uiobject_name = raw_input("UiobjectName: ")
    outName = "\"%s(%s)-%s_%s.launch\" %s (\"%s\", 'warm' if a[0].warm_launch else 'cold', ic.board(), ic.release())" % ("%s", "%s", "%s", "%s", "%", re.sub("\s", "_", uiobject_name))
    args["layer"] = layer
    args["packageName"] = packageName
    args["outName"] = outName
    args["uiobject_name"] = uiobject_name
    uiobject_name = re.sub(r"\s+", "_", uiobject_name)
    return args


def writeHeader(outfd):
    path = "%s/%s" % (sys.path[0], "header")
    fd = open(path, "r")
    content = fd.readlines()
    for line in content:
        outfd.write(line)
    outfd.write("# %s\n" % ("-" * 100))


def writeArgs(outfd, args):
    for key in args.keys():
        if key == "outName":
            line = "args[\"%s\"] = %s\n" % (key, str(args.get(key)))
        else:
            line = "args[\"%s\"] = \"%s\"\n" % (key, str(args.get(key)))
        outfd.write(line)
    outfd.write("# %s\n" % ("-" * 100))
    outfd.write("doQALaunchTime(args)")


def update_scripts():
    l_script = []
    for p, d, f in os.walk(sys.path[0]):
        for py in f:
            if py[-2:] == "py" and py != "launch_script_generator.py":
                l_script.append(os.path.join(p, py))
    for script in l_script:
        arg_lines = []
        with open(script, "r") as f:
            t = f.readlines()
            arg_line_bound = []
            for i in xrange(len(t)):
                if t[i].strip() == "# %s" % ("-" * 100):
                    arg_line_bound.append(i)
            if arg_line_bound == []:
                continue
            arg_lines = t[arg_line_bound[0] + 1: arg_line_bound[1]]
        with open(script, "w") as f:
            writeHeader(f)
            for line in arg_lines:
                f.write(line)
            f.write("# %s\n" % ("-" * 100))
            f.write("doQALaunchTime(args)")


def main():
    if platform.system() != "Linux":
        return
    p = ArgumentParser(usage='launch_script_generator.py [-u]', description='Author wxl')
    p.add_argument('-u', action='store_true', dest='update')
    a = p.parse_known_args(sys.argv)
    if a[0].update:
        update_scripts()
        return 0
    args = getArgs()
    fn_script = "%s_launch.py" % (re.sub("\s", "_", args.get("uiobject_name")))
    fn_path = "%s/%s" % (sys.path[0], fn_script)
    fd = open(fn_path, "w")
    writeHeader(fd)
    fd.write("\n")
    fd.write("\n")
    writeArgs(fd, args)
    fd.close()
    cmd = "chmod +x %s " % fn_path
    os.system(cmd)


if __name__ == '__main__':
    main()
