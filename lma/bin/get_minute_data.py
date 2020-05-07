#!/usr/bin/env python
import multiprocessing as mp
import subprocess as sp
import datetime
import time
import glob
import sys
import os
import errno
import numpy as np
import gzip
import datetime
import calendar
import pyproj

home = os.environ['HOME']
fp = open(home + "/lma/lma_config","r")

for line in fp:
    if (line.startswith("gps_file:")):
        locfile = home + "/lma/loc/" + line.split()[1]
    if (line.startswith("prefix:")):
        prefix = line.split()[1]

tmp_dir = home + "/lma/incoming"  # Whre the rt_final files go
datadir = home +"/lma/realtime/rt_data"  # Where the decimated data files go
resultbase = home +"/lma/realtime/processed_data"
analname = home +"/lma/bin/lma_analysis"
display_dir = home +"/lma/display"
makeImagesProg = display_dir + "/makeLmaImages.py"

#
# Function to create a directory with parents if needed 
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def parse_lma(in_name,out_name):
    if (sys.version[0] == '2'):
        fp = gzip.open(in_name,'rb')
    else:
        fp = gzip.open(in_name,'rt')
    line = fp.readline()
    i = 0
    while (not line.startswith("*** data ***")):
        line = fp.readline()
        if (line.startswith("Data start time:")):
            ll = line.split()
            month = int(ll[-2].split("/")[0])
            mday = int(ll[-2].split("/")[1])
            year = int(ll[-2].split("/")[2])+2000
            dt = datetime.datetime(year = year, month = month, day=mday)
            day_start = calendar.timegm(dt.utctimetuple())

        if (line.startswith("Number of events:")):
            num_events = int(line.split()[-1])
        if (line.startswith("Coordinate center (lat,lon,alt):")):
            clat = float(line.split()[-3])
            clng = float(line.split()[-2])
    lma = np.empty((num_events, 11))
    if (num_events == 0):
        np.save(out_name, lma) 
        return 
    i = 0
    for line in fp:
        linelist = line.split()
        lma[i,0] = float(day_start)     # Unix seconds for start of day
        lma[i,1] = float(linelist[0])   # Seconds after midnight
        lma[i,2] = float(linelist[1])   # Latitude
        lma[i,3] = float(linelist[2])   # Longitude
        lma[i,4] = float(linelist[3])   # Altitude
        lma[i,5] = float(linelist[4])   # Chi^2
        lma[i,6] = float(linelist[5])   # Power
        x = int(linelist[6],16)
        lma[i,7] = float(x)             # Station Mask
        x = int(linelist[6],16)
        count = 0
        while x:
            x &= x-1
            count +=1
        lma[i,8] = float(count)       # Number of stations
        lma[i,9] = 0.0                # x 
        lma[i,10] = 0.0               # y
        i = i+1
    fp.close()

    g = pyproj.Geod(ellps='WGS84')
    ones = np.ones((num_events,1))
    (az,raz,r) = g.inv(clng*ones,clat*ones,lma[:,3],lma[:,2])
    lr  = np.array(r, dtype='double').reshape(-1,1)
    laz = np.array(az,dtype='double')
    x = lr*np.sin(laz*np.pi/180.0)
    y = lr*np.cos(laz*np.pi/180.0)
    lma[:,9] = x[:,0]
    lma[:,10]=y[:,0]
    np.save(out_name, lma) 
    return

def rebuild_dec(fname):
    """ Rebuild LMA realtime data file from rt_final file """
    fin=open(fname,"rb")
    real_name = fin.read(23)
    fin.read(1)
    yymmdd = real_name[2:8]
    hh = real_name[9:11]
    mm = real_name[11:13]
    path_name = "%s/%s/%s/%s"%(datadir,yymmdd,hh,mm)
    mkdir_p(path_name)
    full_name = "%s/%s/%s/%s/%s"%(datadir,yymmdd,hh,mm,real_name)
    print(full_name)
    fout = open(full_name,"wb")
    fout.write(fin.read())
    fout.close()
    fin.close()
    os.remove(fname)
    return full_name

""" Rebuild all data files. """
minute = time.gmtime().tm_min
pattern = "rt_final_*"
myfiles = glob.glob(tmp_dir + "/" + pattern)
for item in myfiles:
    rebuild_dec(item)

filetime = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
pattern = datadir + filetime.strftime("/%y%m%d/%H/%M") + "/L*dat"
outdir = resultbase + filetime.strftime("/%y%m%d/%H/%M")

''' 
Process the data when there are six or more files available.  Because some files may be slow to come in,
check again after 10 seconds to see if more files come in.  However, make the images only the first time
there are enough files.
'''
tries = 0
num_used = 0
images_made = False
os.chdir(display_dir)
while (tries < 6):
    myfiles = glob.glob(pattern)
    if ((len(myfiles) > 5) and (len(myfiles) > num_used)):
        mkdir_p(outdir)
        if (locfile.endswith(".loc")):
            cmd = analname + filetime.strftime(" -d %Y%m%d -t %H%M00 ") + " -s 60 -n 5 --outpu-tag=" + prefix + " -l " + locfile + " -o " + outdir + " " + pattern
        elif (locfile.endswith(".gps")):
            cmd = analname + filetime.strftime(" -d %Y%m%d -t %H%M00 ") + " -s 60 -n 5 --output-tag=" + prefix + " -g " + locfile + " -o " + outdir + " " + pattern
        else:
            print("Invalid location file format: " + locfile)
            sys.exit()
        print cmd
        p = sp.Popen(cmd,shell=True)
        p.wait()
        in_name = glob.glob(outdir + "/*gz")[0]
        base_name = in_name.split("/")[-1]
        np_name = "/home/lma_admin/lma/recent/" + base_name[:-7] + ".npy"
        parse_lma(in_name,np_name)
        
        if (not images_made):
            cmd = makeImagesProg + filetime.strftime(" %y %m %d %H %M")
            print cmd
            p = sp.Popen(cmd.split())
            p.wait()
            images_made = True
        num_used = len(myfiles)
    tries = tries + 1
    time.sleep(10)
