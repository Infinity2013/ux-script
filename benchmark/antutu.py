import os
import sys
import subprocess
import re
from uiautomator import device as d
import xml.etree.cElementTree as ET
from adb import adb
from pprint import pprint
import time


def parse(name):
    scores = {}
    tree = ET.parse(name)
    root = tree.getroot()
    for child in root[0]:
        if child.tag not in ["cpu", "model", "version", "hash", "date"]:
            scores[child.tag] = int(child.text)
    return scores

def getlast():
    p = subprocess.Popen("adb shell \"ls /sdcard/.antutu/benchmark/history_scores\" | tail -1",
            shell=True, stdout=subprocess.PIPE)
    out = p.stdout.readlines()
    if len(out) != 1:
        raise ValueError("There is not result under /sdcard/.antutu/benchmark/history_socres")
    out = out[0].strip()
    unix_out = re.sub("\s", "\ ", out)
    print adb.cmd("pull /sdcard/.antutu/benchmark/history_scores/%s ./" % unix_out).communicate()
    time.sleep(2)
    return out

def start():
    bounds = d(resourceId="com.antutu.ABenchMark:id/pager").child_selector(className="android.widget.ScrollView").child_selector(resourceId="com.antutu.ABenchMark:id/start_test_region").info.get("bounds")
    x = (bounds.get("left") + bounds.get("right")) / 2
    y = (bounds.get("top") + bounds.get("bottom")) / 2
    d.click(x, y)

def stop():
    d(text="STOP").click()

def details():
    d(text="Details").click()

def testagain():
    d(text="Test Again").click()

def main():
    

if __name__ == '__main__':
    main()
