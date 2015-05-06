import subprocess
import os
import sys
import re
from clog import clog
import platform
clog = clog()
clog.setLevel("v|e")
def formatcheck(string):
    if not re.findall("^\S+$", string.strip()):
        return False
    else:
        return True

def versioncheck():
    if platform.system() != "Linux":
        return
    clog.v("Checking updates!")
    os.system("git reset HEAD --hard")
    os.system("git remote update")
    p = subprocess.Popen("git rev-parse HEAD", shell = True, stdout = subprocess.PIPE)
    local_sha = p.stdout.readline().strip()
    if not formatcheck(local_sha):
        clog.e("Couldn't get local head!")
        return
    p = subprocess.Popen("git rev-parse @{u}", shell = True, stdout = subprocess.PIPE)
    remote_sha = p.stdout.readline().strip()
    if not formatcheck(remote_sha):
        clog.e("Couldn't get remote head!")
        return
    if local_sha != remote_sha:
        clog.v("Syncing updates!")
        os.chdir(sys.path[0])
        p = subprocess.Popen("git pull", shell = True, stdout = subprocess.PIPE)
        if p.returncode != 0:
            clog.e("Sync failed!")
        else:
            clog.v("Sync done!")
            clog.v("Please run script again!")
    else:
        clog.v("Already update-latest!")
