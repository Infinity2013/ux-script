adb reboot ptest_clear
adb wait-for-device
adb reboot ptest
adb wait-for-device
adb root
sleep 3
adb shell setenforce 0
adb shell "at_cli_client 'at@wlan_mvt:add_mac_address_command({10,11,173,13,255,255})'"
adb shell "at_cli_client 'at@wlan_mvt:read_mac_address_command()'"
adb shell "at_cli_client 'at@BT:write_nvm_bdaddr({255,255,222,34,34,00})'"
adb shell "at_cli_client 'at@BT:read_nvm_bdaddr()'"
adb shell "at_cli_client 'at@ROCS:LoadAndStartFlow(\"lhp_wifi_calibration\")'"
adb reboot ptest_clear

