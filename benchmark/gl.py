from uiautomator import device as d
from adb import adb
from benchmarkbase import benchmarkbase
import time
import re


class glbenchmark(benchmarkbase):

    def __init__(self, subcase='C24Z16 Offscreen ETC1', duration=90):
        self.dict = {}
        self.dict['title'] = subcase
        self.dict['duration'] = int(duration)

    def prepare(self):
        # kill process
        adb.cmd("shell am force-stop com.glbenchmark.glbenchmark27")
        time.sleep(2)
        # start process
        adb.cmd("shell am start com.glbenchmark.glbenchmark27/com.glbenchmark.activities.GLBenchmarkDownloaderActivity")
        time.sleep(2)

    def clearchoice(self):
        d(text="All").click()
        time.sleep(1)
        d(text="None").click()
        time.sleep(1)

    def check(self, text):
        if d(text=text).exists:
            d(text=text).click()
        else:
            d(scrollable=True).fling.toEnd()
            if d(text=text).exists:
                d(text=text).click()
            else:
                raise ValueError("Can't locate icon %s" % text)

    def start(self):
        d(text="Performance Tests").click()
        time.sleep(2)

    def result(self):
        g = re.match(r'(?P<fps>[\d\.]+)\s*fps$',\
                     self.res_id_text("com.glbenchmark.glbenchmark27:id/textViewFps").strip())
        if g is not None:
            self.dict['fps'] = float(g.group('fps'))
        else:
            raise ValueError("Can't get fps'")
        return self.dict

    def docase(self):
        self.prepare()
        self.clearchoice()
        self.check(self.dict['title'])
        self.start()
        time.sleep(self.dict['duration'])
        return self.result()
