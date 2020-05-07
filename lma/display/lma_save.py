#!/usr/bin/env python

import numpy as np
import lma_util
from lma_util import LmaStation,LmaNetwork,LmaSource,NldnStroke
import os
import gzip
import sys
import state
import datetime
from datetime import timezone
import glob
import pyproj

# Function to read LMA raw data files
def ReadLmaFile(fname):
    ind = fname.rfind(os.path.sep)
    if (fname.endswith(".gz")):
        if (sys.version[0] == '2'):
            fp = gzip.open(fname,'rb')
        else:
            fp = gzip.open(fname,'rt')
    else:
        fp = open(fname,'r')
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
            day_start = dt.replace(tzinfo=timezone.utc).timestamp()

        if (line.startswith("Number of events:")):
            num_events = int(line.split()[-1])
        if (line.startswith("Coordinate center (lat,lon,alt):")):
            clat = float(line.split()[-3])
            clng = float(line.split()[-2])
    lma = np.empty((num_events, 11))
    if (num_events == 0):
        return lma
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
    #print(lma[0,0],lma[0,1],lma[0,2],lma[0,3],lma[0,4],lma[0,5],lma[0,6],lma[0,7],lma[0,8],lma[0,9],lma[0,10])
    #print(lma[-1,0],lma[-1,1],lma[-1,2],lma[0,3],lma[-1,4],lma[-1,5],lma[-1,6],lma[-1,7],lma[-1,8],lma[-1,9],lma[-1,10])
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

    return lma


myfiles = sorted(glob.glob("/home/lma_admin/lma/realtime/processed_data/200422/15/*/*gz"))
for myfile in myfiles:
    print(myfile)
    ll = myfile.split("/")
    outname = "/home/lma_admin/lma/recent/" + ll[-1][:-6] + "npy"
    print(outname)
    lma = ReadLmaFile(myfile)

    np.save(outname, lma) 
sys.exit()

myfiles = sorted(glob.glob("/home/lma_admin/lma/recent/*npy"))
for myfile in myfiles:
    #print(myfile)
    lma = np.load(myfile)
    #print(lma[0,0],lma[0,1],lma[0,2],lma[0,3],lma[0,4],lma[0,5],lma[0,6],lma[0,7],lma[0,8],lma[0,9],lma[0,10])
    #print(lma[-1,0],lma[-1,1],lma[-1,2],lma[0,3],lma[-1,4],lma[-1,5],lma[-1,6],lma[-1,7],lma[-1,8],lma[-1,9],lma[-1,10])


