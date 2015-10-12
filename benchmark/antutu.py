#!/usr/bin/env python
from uiautomator import device as d
from adb import adb
from benchmarkbase import benchmarkbase
import time


class Antutu(benchmarkbase):

    def __init__(self, duration=240):
        self.res_dict = {}
        self.res_dict['title'] = "Antutu5.6"
        self.res_dict['duration'] = duration

    def prepare(self):
        adb.cmd('shell am force-stop com.antutu.ABenchMark').communicate()
        adb.root()
        for cache in ['app_data', 'cache', 'database', 'databases', 'files',
                      'lastscore.dat', 'pid_file', 'shared_prefs']:
            adb.cmd("shell rm -rf /data/app/com.antutu.ABenchMark/%s" % cache)
        adb.cmd('shell am start com.antutu.ABenchMark/.ABenchMarkStart').communicate()

    def start(self):
        if d(resourceId="com.antutu.ABenchMark:id/start_test_text").exists:
            print "test"
            d(resourceId="com.antutu.ABenchMark:id/start_test_text").click()
        elif d(resourceId="com.antutu.ABenchMark:id/retest_text").exists:
            print "again"
            d(resourceId="com.antutu.ABenchMark:id/retest_text").click()
        else:
            raise ValueError('Could find start element')

    def stop(self):
        d(text="STOP").click()

    def details(self):
        d(text="Details").click()

    def result(self):
        # multitask score
        self.res_dict["multitask"] =\
            self.res_id_text("com.antutu.ABenchMark:id/ue_multitask_text")
        # runtime score
        self.res_dict['runtime'] =\
            self.res_id_text('com.antutu.ABenchMark:id/ue_dalvik_text')
        # cpu integer score
        self.res_dict['integer'] =\
            self.res_id_text('com.antutu.ABenchMark:id/cpu_int_text')
        # cpu float score
        self.res_dict['float'] =\
            self.res_id_text('com.antutu.ABenchMark:id/cpu_float_text')
        # single integer score
        self.res_dict['single_integer'] =\
            self.res_id_text('com.antutu.ABenchMark:id/cpu_int_text2')
        # single float score
        self.res_dict['single_float'] =\
            self.res_id_text('com.antutu.ABenchMark:id/cpu_float_text2')
        # ram operation
        self.res_dict['ram_operation'] =\
            self.res_id_text('com.antutu.ABenchMark:id/mem_text')
        # ram speed
        self.res_dict['ram_speed'] =\
            self.res_id_text('com.antutu.ABenchMark:id/ram_text')
        # 2d score
        self.res_dict['2d'] =\
            self.res_id_text('com.antutu.ABenchMark:id/gpu_2d_text')
        # 3d score
        t = self.res_id_text('com.antutu.ABenchMark:id/gpu_3d_text')
        index = t.index(']')
        self.res_dict['3d'] = t[index + 1:]
        # storage score
        self.res_dict['storage'] =\
            self.res_id_text('com.antutu.ABenchMark:id/io_sdw_text')
        # database score
        self.res_dict['database'] =\
            self.res_id_text('com.antutu.ABenchMark:id/io_db_text')
        # total
        self.res_dict['total'] =\
            str(sum(map(int, [val for val in self.res_dict.values()])))
        return self.res_dict

    def docase(self):
        self.prepare()
        time.sleep(3)
        self.start()
        time.sleep(self.res_dict['duration'])
        self.details()
        return self.result()
