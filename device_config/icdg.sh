function echo_and_check {
    # adb shell "echo $1 > $2"
    res=$(adb shell "cat $2")
    echo $res
    if [[ $res == $1 ]];
    then
        echo "SUCCESS"
    else
        echo "FAILED"
    fi
}
echo_and_check '1040000' '/sys/devices/system/cpu/cpufreq/interactive/hispeed_freq'
echo_and_check '95'  '/sys/devices/system/cpu/cpufreq/interactive/target_loads'
echo_and_check '200000'  '/sys/devices/system/cpu/cpufreq/interactive/timer_slack'

