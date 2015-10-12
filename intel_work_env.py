#!/usr/bin/env python
import subprocess
import os
import sys

PROXY = "child-prc.intel.com"
PORT = "913"
LOCAL_MIRROR = "android-mirror-sh.devtools.intel.com"
LOCAL_MIRROR_ADDRESS = "10.239.29.68"
IDSID = "wuxiaolx"
EMAIL = "xiaoliangx.wu@intel.com"
HOME = os.environ.get("HOME")
def setproxy():
    global PROXY, PORT
    protocollist = ['http', 'https', 'ftp', 'socks']
    # set proxy
    for protocol in protocollist:
        # set host
        cmd = "dconf write /system/proxy/%s/host \"'%s'\"" % (protocol, PROXY)
        print cmd
        os.system(cmd)
        # set port
        cmd = "dconf write /system/proxy/%s/port \"'%s'\"" % (protocol, PORT)
        print cmd
        os.system(cmd)
    # set ignore list
    cmd = "dconf write /system/proxy/ignore-hosts \"['localhost', '127.0.0.0/8', '::1', '*.intel.com']\""
    os.system(cmd)

def setgitconfig():
    content = '\
     [url "ssh://YOUR_IDSID@YOUR_LOCAL_MIRROR:29418/"]\n\
     insteadOf=git://android.intel.com/\n\
     insteadOf=ssh://android.intel.com/\n\
     insteadOf=ssh://android.intel.com:29418/\n\
     insteadOf=git://android-mirror.devtools.intel.com/\n\
     insteadOf=ssh://android-mirror.devtools.intel.com/\n\
     insteadOf=ssh://android-mirror.devtools.intel.com:29418/\n\
     insteadOf=git://jfumg-gcrmirror.jf.intel.com/\n\
     insteadOf=ssh://jfumg-gcrmirror.jf.intel.com/\n\
     insteadOf=git://<YOUR_LOCAL_MIRROR>/\n\
     insteadOf=ssh://<YOUR_LOCAL_MIRROR>/\n\
     insteadOf=ssh://<YOUR_LOCAL_MIRROR>:29418/\n\
      \n\
      \n\
     [url "ssh://YOUR_IDSID@android.intel.com:29418/"]\n\
     pushInsteadOf=ssh://android.intel.com/\n\
     pushInsteadOf=ssh://android.intel.com:29418/\n\
     pushInsteadOf=ssh://android-mirror.devtools.intel.com/\n\
     pushInsteadOf=ssh://android-mirror.devtools.intel.com:29418/\n\
     pushInsteadOf=ssh://jfumg-gcrmirror.jf.intel.com/\n\
     pushInsteadOf=ssh://jfumg-gcrmirror.jf.intel.com:29418/\n\
     pushInsteadOf=ssh://<YOUR_LOCAL_MIRROR>/\n\
     pushInsteadOf=ssh://<YOUR_LOCAL_MIRROR>:29418/'
    content = content.replace("YOUR_IDSID", IDSID)
    content = content.replace("<YOUR_LOCAL_MIRROR>", LOCAL_MIRROR)
    content = content.replace("YOUR_LOCAL_MIRROR", LOCAL_MIRROR)
    with open("%s/.gitconfig" % HOME, "w") as f:
        f.write(content)
    os.system('git config --global user.name "%s"' % IDSID)
    os.system('git config --global user.email "%s"' % EMAIL)

def setsshconfig():
    content = '\
    host android.intel.com\n\
        port 29418\n\
        user <IDSID>\n\
      \n\
    host jfumg-gcrmirror.jf.intel.com\n\
        port 29418\n\
        user <IDSID>\n\
        StrictHostKeyChecking no\n\
\n\
    host android-mirror*.devtools.intel.com\n\
        port 29418\n\
        user <IDSID>   \n\
        StrictHostKeyChecking no\n\
\n\
    host <YOUR_LOCAL_MIRROR>\n\
        port 29418\n\
        user <IDSID>'
    content = content.replace("<IDSID>", IDSID)
    content = content.replace("<YOUR_LOCAL_MIRROR>", LOCAL_MIRROR)
    with open("%s/.ssh/config" % HOME, "w") as f:
        f.write(content)
    os.system("chmod 600 %s/.ssh/config" % HOME)

def keyscan():
    os.system('ssh-keyscan -p 29418 android.intel.com >> ~/.ssh/known_hosts')
    os.system('ssh-keyscan -p 29418 %s >> ~/.ssh/known_hosts' % LOCAL_MIRROR)
    os.system('ssh-keyscan -p 29418 %s >> ~/.ssh/known_hosts' % LOCAL_MIRROR_ADDRESS)
    os.system('ssh android.intel.com gerrit ls-projects', shell=True, stdout=subprocess.PIPE)
    

def sshkeygen():
    cmd = 'rm %s/.ssh/py_rsa*' % HOME
    os.system(cmd)
    cmd = 'ssh-keygen -f %s/.ssh/py_rsa -N ""' % HOME
    os.system(cmd)
    py_rsa_pub = ""
    with open("%s/.ssh/py_rsa.pub" % HOME, "r") as f:
        py_rsa_pub = f.readline().strip()
    return py_rsa_pub

def main():
#    sshkeygen()
#    setproxy()
    setgitconfig()
    setsshconfig()
    keyscan()

if __name__ == "__main__":
    main()
	
	
