#!/usr/bin/env python
import pyproj
import numpy as np
import os
import gzip
import sys
import shapefile as shp

class LmaStation:
    lat = 0.0
    lng = 0.0
    alt = 0.0
    letter = ""
    name = ""
    active = False

class LmaNetwork:
    ctr_lat = 0.0
    ctr_lng = 0.0
    station = []
    location = ""

class NldnStroke:
    time = np.datetime64("1970-01-01T00:00:00.00",dtype='datetime64[ns]')
    lat = 0.0
    lng = 0.0
    i = 0.0
    flash_type = ""
    marker_type = ""

    def calc_xy(self, network):
        g = pyproj.Geod(ellps='WGS84')
        (az, raz, dist) = g.inv(network.ctr_lng, network.ctr_lat, self.lng, self.lat)
        x = dist*np.sin(az*np.pi/180.0)
        y = dist*np.cos(az*np.pi/180.0)
        return(x,y)


class LmaSource:
    time = np.datetime64("1970-01-01T00:00:00.00",dtype='datetime64[ns]')
    lat = 0.0
    lng = 0.0
    alt = 0.0
    chi2 = 0
    pwr = 0
    mask = ""
    num_sta = 0
    x = 0.0
    y = 0.0
    r = 0.0

def ll2xy(lat, lng, ctr_lat, ctr_lng):
    g = pyproj.Geod(ellps='WGS84')
    (az, raz, dist) = g.inv(ctr_lng, ctr_lat, lng, lat)
    x = dist*np.sin(az*np.pi/180.0)
    y = dist*np.cos(az*np.pi/180.0)
    return x,y

def xy2ll(x, y, ctr_lat, ctr_lng):
    g = pyproj.Geod(ellps='WGS84')
    dist = np.sqrt(x*x + y*y)
    bearing =  np.arctan2(x,y)*180.0/np.pi
    (plng, plat, b2) = g.fwd(ctr_lng, ctr_lat, bearing, dist)
    lng = plng
    lat = plat
    return lat,lng

       
# Concatentate a number of LMA files into a single file
# If the files cross a day boundary, concatenate files based on day
# Filenames must be in form "NETWORK_yymmdd_hhmmss_ssss.dat.gz"
#NETWORK_yymmdd_hhmmss_ssss.dat.gz
#    98765432109876543210987654321
def LmaConcatenate(flist):
    start_str = ""
    for fname in flist:
        if (fname[:-25] != start_str):
            # Start of a new day.  Get new header info
            if (start_str != ""):
                # Already had files.  This is a new day.  Write out yesterday's file
                ts = str(t_start_overall)
                num_sec = int((t_end_overall-t_start_overall)/np.timedelta64(1,'s'))
                if (num_sec > 9999):
                    t_start_overall = t_end - np.timedelta64(9999.0,'s')
                    num_sec = 9999
                num_sec_str = ("_%04d.dat.gz") % (num_sec)
                fname_out = start_str + ts[2:4] + ts[5:7] + ts[8:10] + "_" + ts[11:13] + ts[14:16] + ts[17:19] + num_sec_str
                header_list[start_line] = "Data start time: " + ts[5:7] + "/" + ts[8:10] + "/" + ts[2:4] + " " + ts[11:13] + ":" + ts[14:16] + ":" + ts[17:19] + "\n"
                header_list[num_events_line] = "Number of events: " + str(len(source_list)) + "\n"
                header_list[num_secs_line] = "Number of seconds analyzed: " + str(num_sec) + "\n"
                if (sys.version[0] == '2'):
                    fout = gzip.open(fname_out,"w")
                else:
                    fout = gzip.open(fname_out,"wt")
                for line in header_list:
                    fout.write(line)
                for line in source_list:
                    fout.write(line)
                fout.close()
                header_list = []
                source_list = []
            start_str = fname[:-25]
            header_list = []
            source_list = []
            fname = flist[0]
            start_str = fname[:-25]
            try:
                if (fname.endswith(".gz")):
                    if (sys.version[0] == '2'):
                        fid = gzip.open(fname,'rb')
                    else:
                        fid = gzip.open(fname,'rt')
                else:
                    fid = open(fname,'r')
                line = fid.readline()
                header_list.append(line)
                i = 0
                while (not line.startswith("*** data ***")):
                    if (line.startswith("Data start time:")):
                        t_start_overall = np.datetime64('20' + line[23:25] + '-' + line[17:19] + '-' + line[20:22] + 'T' + line.split()[-1],dtype='datetime64[ns]')
                        start_line = i
                    if (line.startswith("Number of seconds analyzed")):
                        num_secs = int(line.split()[-1])
                        t_end_overall = t_start_overall + np.timedelta64(num_secs,'s')
                        num_secs_line = i
                    if (line.startswith("Number of events:")):
                        num_events_line = i
                    line = fid.readline()
                    header_list.append(line)
                    i = i+1
                for line in fid:
                    source_list.append(line)
                fid.close()
            except IOError:
                pass
            os.remove(fname)
        else:
            try:
                if (fname.endswith(".gz")):
                    if (sys.version[0] == '2'):
                        fid = gzip.open(fname,'rb')
                    else:
                        fid = gzip.open(fname,'rt')
                else:
                    fid = open(fname)
                line = fid.readline()
                while (not line.startswith("*** data ***")):
                    if (line.startswith("Data start time:")):
                        t_start = np.datetime64('20' + line[23:25] + '-' + line[17:19] + '-' + line[20:22] + 'T' + line.split()[-1],dtype='datetime64[ns]')
                        t_start_overall = min(t_start, t_start_overall)
                    if (line.startswith("Number of seconds analyzed")):
                        num_secs = int(line.split()[-1])
                        t_end = t_start + np.timedelta64(num_secs,'s')
                        t_end_overall = max(t_end, t_end_overall)
                    line = fid.readline()
                for line in fid:
                    source_list.append(line)
                fid.close()
            except IOError:
                pass
            os.remove(fname)

    ts = str(t_start_overall)
    num_sec = int((t_end_overall-t_start_overall)/np.timedelta64(1,'s'))
    if (num_sec > 9999):
        t_start_overall = t_end - np.timedelta64(9999.0,'s')
        num_sec = 9999
    num_sec_str = ("_%04d.dat.gz") % (num_sec)
    fname_out = start_str + ts[2:4] + ts[5:7] + ts[8:10] + "_" + ts[11:13] + ts[14:16] + ts[17:19] + num_sec_str
    header_list[start_line] = "Data start time: " + ts[5:7] + "/" + ts[8:10] + "/" + ts[2:4] + " " + ts[11:13] + ":" + ts[14:16] + ":" + ts[17:19] + "\n"
    header_list[num_events_line] = "Number of events: " + str(len(source_list)) + "\n"
    header_list[num_secs_line] = "Number of seconds analyzed: " + str(num_sec) + "\n"
    if (sys.version[0] == '2'):
        fout = gzip.open(fname_out,"w")
    else:
        fout = gzip.open(fname_out,"wt")
    for line in header_list:
        fout.write(line)
    for line in source_list:
        fout.write(line)

def plot_shapefile(shapefile,axis,order=1,clr='0.8',size='f'):
    if (size == 'f'):
        lw = 0.8
    else:
        lw = 0.2
    sf = shp.Reader(shapefile, encoding="latin1")
    for shape in sf.shapeRecords():
        try:
            for i in range(len(shape.shape.parts)):
                i_start = shape.shape.parts[i]
                if i==len(shape.shape.parts)-1:
                    i_end = len(shape.shape.points)
                else:
                    i_end = shape.shape.parts[i+1]
                x = [i[0] for i in shape.shape.points[i_start:i_end]]
                y = [i[1] for i in shape.shape.points[i_start:i_end]]
                axis.plot(x,y,color=clr,zorder=order,linewidth=lw)
        except:
            pass

def plot_datfile(datfile,axis,order=1,clr='0.8',size='f'):
    if (size == 'f'):
        lw = 0.4
    else:
        lw = 0.2
    if (order < 3):
        fid = open(datfile)
        line1 = True
        line_end = False
        boundary_lat = []
        boundary_lng = []
        for line in fid:
            if line1:
                line1=False
                continue
            if (line[0] == "E") and (line_end):
                break
            if (line[0] == "E"):
                line_end = True
                line1 = True
                axis.plot(boundary_lng,boundary_lat,linewidth=lw,color=clr,zorder=order)
                boundary_lat = []
                boundary_lng = []
            else:
                line_end = False
                boundary_lat.append(float(line.split()[1]))
                boundary_lng.append(float(line.split()[0]))
    if (order == 3):
        fid=open(datfile)
        for line in fid:
            lat = float(line.split()[1]) 
            lng = float(line.split()[2])
            axis.plot(lng,lat,'ro',markeredgecolor='r',markerfacecolor='None',markeredgewidth=0.5,markersize=4.0,zorder=3)

def plot_txtfile(txtfile,axis,order=1):
    fid=open(txtfile)
    for line in fid:
        if (line.startswith("#")):
            continue
        lat = float(line.split()[1]) 
        lng = float(line.split()[2])
        axis.plot(lng,lat,'ro',markeredgecolor='#FFC0C0',markerfacecolor='None',markeredgewidth=0.5,markersize=4.0,zorder=order)

