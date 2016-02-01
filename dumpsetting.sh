adb shell settings list system > $1
adb shell settings list global >> $1
adb shell settings list secure >> $1
