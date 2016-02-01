adb shell settings put system screen_brightness 255
adb shell settings put system screen_off_timeout 1800000
adb root
sleep 2
current=$(pwd)
for push in $(find -name "push.sh")
do
	tmp=$(dirname $push)
	cd $tmp
	./push.sh
	cd $current
done
