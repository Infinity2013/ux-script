from uiautomator import device as d
from adb import adb
import time


class quadrant():

    def __init__(self, duration=40):
        self.dict = {}
        self.dict['title'] = 'quadrant2d'
        self.dict['duration'] = duration

    def prepare():
        adb.cmd('shell am force-stop com.aurorasoftworks.quadrant.ui.professional')
        adb.cmd('shell am start com.aurorasoftworks.quadrant.ui.professional/.QuadrantProfessionalLauncherActivity')
        adb.cmd('logcat -c')

