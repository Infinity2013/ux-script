import speech_recognition as sr
from  uiautomator import device as d
info = d(text="Chrome").info.get("bounds")
print info
chrome_x = (info.get("left") + info.get("right")) / 2
y = (info.get("top") + info.get("bottom")) / 2
info = d(text="YouTube").info.get("bounds")
youtube_x = (info.get("left") + info.get("right")) / 2
app_x = (chrome_x + youtube_x) / 2
w = d.info.get("displayWidth")
h = d.info.get("displayHeight")
w_delta = w / 7
h_delta = h / 7
index = 0
for i in xrange(2,7):
    for j in xrange(0, 7):
        d.press.back()
        d.click(app_x, y)
        d(text="Calculator").drag.to(w_delta * j, h_delta * i, steps=20)
