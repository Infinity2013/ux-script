#!/usr/bin/env python
import os
import sys
from argparse import ArgumentParser
import subprocess


def main():
    p = ArgumentParser()
    p.add_argument('-r', dest='repeat', default=0, type=int, help='repeat count')
    p.add_argument('-d', dest='delta', default=0, type=int, help='delta between each excute')
    p.add_argument('-o', dest='output',default=None,  help='output file')
    p.add_argument('--cmd', dest='cmd', default=None, help='executable file')
    p.add_argument('--sh', dest='shell', default=None, help='')
    args = p.parse_known_args(sys.argv)
    repeat = args[0].repeat
    delta = args[0].delta
    output = args[0].output
    cmd = args[0].cmd
    shell = args[0].shell
    if not cmd and not shell:
        print "cmd and shell can't be both None"
        return
    elif cmd and shell:
        print "Error"
        return
    for i in xrange(repeat):
        if output is None:
            os.system()



if __name__ == '__main__':
    main()
