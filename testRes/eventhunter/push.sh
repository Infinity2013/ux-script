adb root
sleep 2
adb push eventHunter /data/eventHunter
adb shell "chmod 777 /data/eventHunter"
