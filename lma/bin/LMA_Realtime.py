#!/usr/bin/python
import subprocess as sp
import time
import os
import sys
import glob
import errno

# Function to create a directory with parents if needed 
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

home = os.environ['HOME']
fid = open(home + "/lma/lma_config","r")
for line in fid:
    if (line.startswith("delay:")):
        delay = int(line.split()[1])
# If $HOME/lma/recent is a symbolic link to a tmpfs filesystem, make sure directory exsists
if (os.path.islink(home + "/lma/recent")):
    mylink = os.readlink(home + "/lma/recent")
    if not os.path.isdir(mylink):
        mkdir_p(mylink)
# If $HOME/lma/tmp is a symbolic link to a tmpfs filesystem, make sure directory exsists
if (os.path.islink(home + "/lma/tmp")):
    mylink = os.readlink(home + "/lma/tmp")
    if not os.path.isdir(mylink):
        mkdir_p(mylink)

while True:
    # Wait until delay seconds after the minute
    secs = time.gmtime().tm_sec
    print(secs)
    if (secs > delay):
        time.sleep(60 + delay - secs)
    elif (secs < delay):
        time.sleep(delay - secs)
    # Remove old .npy files (need last 60 minutes, so keep only last 70 files)
    myfiles = sorted(glob.glob(home + "/lma/recent/*npy"))
    for item in myfiles[:-70]:
        os.remove(item)
    sp.Popen(os.environ['HOME'] + "/lma/bin/get_minute_data.py")
    print("Started get_minute_data.py")
    time.sleep(2)
    
