from adb import Adb
from uiautomator import device as d
import time
'''
work flow
preapre: sleep time && screen lock && setup jio config && reboot
start: drop cache && sync && start process && run case
report: get result
'''

l_item = [
    'Sequential Write',
    'Sequential Read',
    'Random Write',
    'Random Read',
        ]

d_item_sleep = {
    l_item[0]: 200,
    l_item[1]: 200,
    l_item[2]: 250,
    l_item[3]: 320,
                }


def prepare(adb):
    pass


def do_app_config():
    for item in l_item:
        d(text=item).click()
        d(index=5).set_text(1)
        d(text="Save").click()
    d.press.back()
    d(text='Settings').click()
    view = d(text='Keep pretest file after test')
    if not view.info['checked']:
        view.click()
    d(text='Save').click()


def start(item, adb):
    adb.cmd("shell 'echo 3 > /proc/sys/vm/drop_caches'").communicate()
    adb.cmd("shell sync").communicate()
    adb.cmd("shell am start com.intel.jio/.JIO_Activity")
    time.sleep(2)
    d(text='Performance Tests').click()
    d(text='Clear').click()
    d(text=item).click()
    d(text='Run').click()
    time.sleep(d_item_sleep[item])


def report(item):
    logs = d(resourceId="com.intel.jio:id/textViewLogContent").text.splitlines()
    d_tmp = {}
    for log in logs:
        tmp = log.strip().split(":")
        if len(tmp) == 2:
            d_tmp[tmp[0].strip()] = tmp[1].strip()
    return d_tmp[item]


def main():
    d_result = {}
    for case in l_item:
        d_result[case] = []
    adb = Adb()
    prepare(adb)
    for i in xrange(3):
        for item in l_item:
            start(item, adb)
            d_result[case].append(report(item))
            adb.cmd('reboot')
    print d_result


if __name__ == '__main__':
    main()
