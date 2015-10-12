#!/usr/bin/env python
from argparse import ArgumentParser
import sys
import subprocess
from adb import adb
import re
from pprint import pprint
def main():
    p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author wxl')
    p.add_argument('-r', default=5, dest='repeat', type=int, help='repeat')
    a = p.parse_known_args(sys.argv)

    adb.cmd("shell stop").communicate()
    app_home_list, surfaceview_home_list = [], []
    index = 0
    print "index  app->home  surfaceview->home"
    while index < a[0].repeat:
        app_home = adb.cmd("shell /data/flatland -c 0 -b 2 -h 1600").communicate()[0]
        g = re.findall(r'\d+\.\d+', app_home)
        if g is not None:
            app_home_list.append(float(g[0]))
        else:
            raise ValueError("no result in app -> home!")

        surfaceview_home = adb.cmd("shell /data/flatland -c 0 -b 4 -h 1600").communicate()[0]
        g = re.findall(r'\d+\.\d+', surfaceview_home)
        if g is not None:
            surfaceview_home_list.append(float(g[0]))

        print "%-5d %-9f  %-16f" % (index, app_home_list[-1], surfaceview_home_list[-1])
        index += 1

    app_home_list.sort()
    surfaceview_home_list.sort()

    pprint(app_home_list)
    pprint(surfaceview_home_list)


if __name__ == '__main__':
    main()
