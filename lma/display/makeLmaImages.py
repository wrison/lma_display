#!/usr/bin/env python
'''
makeLmaImages.py makes LMA images from realtime LMA data files.

Every minute, ten-minute and two-minute images are created.  Ten-minute images
are for the last ten minutes of LMA data; two-minute images are for the past two
minutes of LMA data.  These images go into the directory
"/var/www/html/NETWORK/current", with names like "current_0600_z1_pts.png".
"0600" means a ten minute (600 second) image, "z1" means zoom level 1, "pts"
means color by points.  The ten-minute files for density also go into
"/var/www/html/NETWORK/current/anim_z?" so they can be made into animations.

Every ten minutes the ten-minute time and density images are saved in the
archive directory "/var/www/html/NETWORK/img/YY/MM/DD/HH"

Every hour one-hour images of time and density are created and saved in the
archive directory "/var/www/html/NETWORK/img/YY/MM/DD/HH"

'''

import os
import sys
import shutil
import gzip
import matplotlib
matplotlib.use('Agg')
import errno
import lma_util
import glob
import  numpy as np
import shapefile as shp
import datetime
import pyproj
import subprocess as sp
import tempfile
import calendar
import random

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from matplotlib.colors import LogNorm
from PIL import Image, ImageOps
import state
from lma_util import LmaStation,LmaNetwork,LmaSource,NldnStroke

# Function to create a directory with parents if needed
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# Function to read configuration file
def ReadConfFile(conf_file):
    fp = open(conf_file,"r")
    home = os.environ['HOME']
    for line in fp:
        if '$HOME' in line:
            line = line.replace('$HOME',home)
        if (line.lower().startswith("location:")):
            state.location = line.split()[1]
        if (line.lower().startswith("www_dir:")):
            state.www_dir = line.split()[1]
        if (line.lower().startswith("prefix:")):
            state.prefix = line.split()[1]
        if (line.lower().startswith("z1:")):
            state.z1 = int(line.split()[1])
        if (line.lower().startswith("z2:")):
            state.z2 = int(line.split()[1])
        if (line.lower().startswith("z3:")):
            state.z3 = int(line.split()[1])
        if (line.lower().startswith("anim_len:")):
            state.anim_len = int(line.split()[1])
        if (line.lower().startswith("gps_file:")):
            state.gps_file = home + "/lma/loc/" + line.split()[1]
        if (line.lower().startswith("nsew_limits:")):
            ll = line.split()
            state.geo_max_lat = float(ll[-4])
            state.geo_min_lat = float(ll[-3])
            state.geo_max_lng = float(ll[-2])
            state.geo_min_lng = float(ll[-1])
        if (line.lower().startswith("url:")):
            state.cbar_url = line.split()[-1] + "/geo_images/" + state.location + "_cbar.png"
            state.image_url = line.split()[-1] + "/geo_images/" + state.location + "_Composite.png"


def Plot_Geo(ax):
    # Uncommment the following line to plot state boundaries on Google Earth.  These lines should match the Google Earth boundary lines
    #ax.plot(state.admin0[:,1],state.admin0[:,0],color='red',zorder=2,linewidth=0.4)
    xedges, yedges= np.linspace(state.geo_min_lng, state.geo_max_lng, 800), np.linspace(state.geo_min_lat, state.geo_max_lat, 800)
    if (len(keep) > 1):
        xy, yedges, xedges = np.histogram2d(state.lma[keep,2],state.lma[keep,3], (yedges,xedges))
    else:
        tmp_lng = [state.geo_min_lng,state.geo_max_lng]
        tmp_lat = [state.geo_min_lat,state.geo_max_lat]
        xy, yedges, xedges = np.histogram2d(tmp_lat,tmp_lng, (yedges,xedges))
    if (np.amax(xy) < 2):
        xy[1,1] = 2
    img = ax.imshow(xy,norm=LogNorm(),cmap=state.den_cm,extent=(state.geo_min_lng,state.geo_max_lng,state.geo_min_lat,state.geo_max_lat),origin='lower',zorder=6,aspect='auto')
    ax.set_xlim(state.geo_min_lng,state.geo_max_lng)
    ax.set_ylim(state.geo_min_lat,state.geo_max_lat)
    ax.set_xlabel('Longitude',size=10)
    ax.xaxis.set_label_coords(0.5,-0.055,transform=ax.transAxes)
    ax.set_ylabel('Latitude',size=10)
    plt.axis('off')  # Turn of axis box -- don't want for Google Earth overlay
    trans = True
    # Get rid of white space around plot
    temp_name = "/dev/shm/" + next(tempfile._get_candidate_names()) + ".png"
    plt.savefig(temp_name,transparent=trans,bbox_inches='tight',pad_inches=0,dpi=200)
    fig,ax = plt.subplots(figsize=(8.0,3.0))
    cbar = plt.colorbar(img,ax=ax,orientation='horizontal')
    cbar.set_label("$Sources/km^2$",fontsize=12,labelpad=-5)
    ax.remove()
    plt.savefig(state.www_dir + "/geo_images/" + state.location + "_cbar.png",transparent=trans,bbox_inches='tight',pad_inches=0)
    # Python 2 didn't crop image properly.  Manually crop it if necessary.
    img = Image.open(temp_name)
    width,height=img.size
    if (width > 1600):
        img2 = img.crop((width-1600,0,width,1600))
        img2.save(state.www_dir + "/geo_images/" + state.location + "_Composite.png")
        if state.do_eol_upload:
            img2.save(state.www_dir + "/geo_images/" + state.eol_pngname)
    else:
        img.save(state.www_dir + "/geo_images/" + state.location + "_Composite.png")
        if state.do_eol_upload:
            img.save(state.www_dir + "/geo_images/" + state.eol_pngname)

# Function to plot plan position data.  Can plot color by points, color by time, or density.  Can make large plots or small plots
# thumbnails.
def Plot_Plan(ax,p_type,size):
    if (size == 'f'):
        station_marker_size = 4.0
        point_marker_size = state.marker_size
    else:
        station_marker_size = 1.0
        point_marker_size = state.thumb_marker_size
    ax.cla()
    # Plot background data on plan view
    ax.plot(state.stations[:,1],state.stations[:,0],'gs',markeredgecolor='#80FF37',markerfacecolor='None',markeredgewidth=1.0,markersize=station_marker_size,zorder=4)
    if (size == 'f'):
        lw = 0.4
    else:
        lw = 0.1
    if ('admin0' in state.data.keys()):
        morder = 2
        color = 'red'
        ax.plot(state.admin0[:,1],state.admin0[:,0],color=color,zorder=morder,linewidth=lw)
    if ('admin1' in state.data.keys()):
        morder = 1
        color = '0.8'
        ax.plot(state.admin1[:,1],state.admin1[:,0],color=color,zorder=morder,linewidth=lw)
    if ('poi' in state.data.keys()):
        morder = 1
        ax.plot(state.poi[:,1],state.poi[:,0],'ro',markeredgecolor='#FFC0C0',markerfacecolor='None',markeredgewidth=0.5,markersize=4.0,zorder=morder)

    if (len(keep) > 1):  # Plot only if there is data
        if (p_type == 't'):
            clma=((state.lma_t[keep]-state.lma_t[keep[0]])/(state.lma_t[keep[-1]]-state.lma_t[keep[0]]))
            ax.scatter(state.lma[keep,3],state.lma[keep,2],marker='D',c=clma,s=point_marker_size,cmap=state.lma_cmap,edgecolors='none')
            #ax.scatter(lma_x[keep]/1000.0,lma_y[keep]/1000.0,marker='D',c=clma,s=point_marker_size,cmap=state.lma_cmap)
        elif (p_type == 'p'):
            clma = np.arange(len(keep))/float(len(keep))
            ax.scatter(state.lma[keep,3],state.lma[keep,2],marker='D',c=clma,s=point_marker_size,cmap=state.lma_cmap,edgecolors='none')
            #ax.scatter(lma_x[keep]/1000.0,lma_y[keep]/1000.0,marker='D',c=clma,s=point_marker_size,cmap=state.lma_cmap)
        else:
            xedges, yedges= np.linspace(min_lng, max_lng, 450/1.5), np.linspace(min_lat, max_lat, 450/1.5)
            #xedges, yedges= np.linspace(-pz, pz, 450/1.5), np.linspace(-pz, pz, 450/1.5)
            xy, yedges, xedges = np.histogram2d(state.lma[keep,2],state.lma[keep,3], (yedges,xedges))
            #xy, yedges, xedges = np.histogram2d(lma_x[keep]/1000.0,lma_y[keep]/1000.0, (yedges,xedges))
            if (np.amax(xy) < 2):
                xy[1,1] = 2   # If at most one source per pixel LogNorm doesn't plot correctly; set one pixel to have two sources
            ax.imshow(xy,norm=LogNorm(),cmap=state.den_cm,extent=(min_lng,max_lng,min_lat,max_lat),origin='lower',zorder=6,aspect='auto')


    ax.set_xlim(min_lng,max_lng)
    #ax.set_xlim(-pz,pz)
    ax.set_ylim(min_lat,max_lat)
    #ax.set_ylim(-pz,pz)
    ax.set_xlabel('Longitude',size=8)
    #x.set_xlabel('East-West, km',size=10)
    ax.xaxis.set_label_coords(0.5,-0.055,transform=ax.transAxes)
    ax.set_ylabel('Latitude',size=8)
    #ax.set_ylabel('North-South, km',size=10)

# Plot NS vs altitude, color by points, color by time or density
def Plot_NS(ax,p_type):
        ax.cla()
        size = state.marker_size*2.0
        ax.yaxis.set_label_position("right")

        if (len(keep) > 1):  # Plot only if there is data
            if (p_type == 't'):
                clma=((state.lma_t[keep]-state.lma_t[keep[0]])/(state.lma_t[keep[-1]]-state.lma_t[keep[0]]))
                ax.scatter(state.lma[keep,4]/1000.0,state.lma[keep,10]/1000.0,s=size,marker='D',c=clma,edgecolors='none',cmap=state.lma_cmap,zorder=6)
            elif (p_type == 'p'):
                clma = np.arange(len(keep))/float(len(keep))
                ax.scatter(state.lma[keep,4]/1000.0,state.lma[keep,10]/1000.0,s=size,marker='D',c=clma,edgecolors='none',cmap=state.lma_cmap,zorder=6)
            else:
                zedges, yedges= np.linspace(0.0, 20.0, 100/1.5), np.linspace(-pz, pz, 450/1.5)
                yz, yedges, zedges = np.histogram2d(state.lma[keep,10]/1000.0,state.lma[keep,4]/1000.0, (yedges,zedges))
                if (np.amax(yz) < 2):
                    yz[1,1] = 2   # If at most one source per pixel LogNorm doesn't plot correctly; set one pixel to have two sources
                ax.imshow(yz,norm=LogNorm(),cmap=state.den_cm,extent=(0.0,20.0,-pz,pz),origin='lower',zorder=6,aspect='auto')

        ax.set_xlim(0.0,20.0)
        ax.set_ylim(-pz,pz)
        ax.set_xlabel('Altitude, km',size=8)
        ax.set_ylabel('North-South, km',size=8)
        ax.xaxis.set_label_coords(0.5,-0.055,transform=ax.transAxes)
        ax.grid(True)

# Plot EW vs altitude, color by points, color by time or density
def Plot_EW(ax,p_type):
        ax.cla()
        size = state.marker_size*2.0

        if (len(keep) > 1):   # Plot only if there is data
            if (p_type == 't'):
                clma=((state.lma_t[keep]-state.lma_t[keep[0]])/(state.lma_t[keep[-1]]-state.lma_t[keep[0]]))
                ax.scatter(state.lma[keep,9]/1000.0,state.lma[keep,4]/1000.0,marker='D',c=clma,s=size,edgecolors='none',cmap=state.lma_cmap,zorder=6)
            elif (p_type == 'p'):
                clma = np.arange(len(keep))/float(len(keep))
                ax.scatter(state.lma[keep,9]/1000.0,state.lma[keep,4]/1000.0,marker='D',c=clma,s=size,edgecolors='none',cmap=state.lma_cmap,zorder=6)
            else:
                xedges, zedges= np.linspace(-pz , pz, 450/1.5), np.linspace(0.0, 20.0, 100/1.5)
                xz, zedges, xedges = np.histogram2d(state.lma[keep,4]/1000.0,state.lma[keep,9]/1000.0, (zedges,xedges))
                if (np.amax(xz) < 2):
                    xz[1,1] = 2   # If at most one source per pixel LogNorm doesn't plot correctly; set one pixel to have two sources
                ax.imshow(xz,norm=LogNorm(),cmap=state.den_cm,extent=(-pz,pz,0.0,20.0),origin='lower',zorder=6,aspect='auto')

        ax.set_ylim(0.0,20.0)
        ax.set_xlim(-pz,pz)
        ax.set_ylabel('Altitude, km',size=8)
        ax.set_xlabel('East-West, km',size=8)
        ax.yaxis.set_label_coords(-0.05,0.5)
        ax.xaxis.set_label_coords(0.5,-0.12,transform=ax.transAxes)
        ax.grid(True)

# Plot Time vs altitude, color by points, color by time or density
def Plot_TA(ax,p_type):
        ax.cla()
        size = state.marker_size
        if (len(keep) > 1):   # Plot only if there is data
            if (p_type == 'p'):
                clma = np.arange(len(keep))/float(len(keep))
                ax.scatter((state.lma[keep,0] - state.lma[0,0]) + state.lma[keep,1] - start_time_sec,state.lma[keep,4]/1000.0,marker='D',c=clma,cmap=state.lma_cmap,s=size,edgecolors='none')
            elif (p_type == 't'):
                clma=((state.lma_t[keep]-state.lma_t[keep[0]])/(state.lma_t[keep[-1]]-state.lma_t[keep[0]]))
                ax.scatter((state.lma[keep,0] - state.lma[0,0]) + state.lma[keep,1] - start_time_sec,state.lma[keep,4]/1000.0,marker='D',c=clma,cmap=state.lma_cmap,s=size,edgecolors='none')
            else:
                tedges, zedges= np.linspace(0.0, end_time_sec - start_time_sec, 450/2), np.linspace(0.0, 20.0, 100)
                tz, zedges, tedges = np.histogram2d(state.lma[keep,4]/1000.0, (state.lma[keep,0] - state.lma[0,0]) + state.lma[keep,1] - start_time_sec, (zedges,tedges))
                if (np.amax(tz) < 2):
                    tz[1,1] = 2   # If at most one source per pixel LogNorm doesn't plot correctly; set one pixel to have two sources
                ax.imshow(tz,norm=LogNorm(),cmap=state.den_cm, extent=(0, end_time_sec-start_time_sec, 0.0,20.0),
                          origin='lower',zorder=6,aspect='auto')

        ax.axis([0.0, end_time_sec-start_time_sec,  0.0, 20.0])
        ax.grid(True)
        ax.set_ylabel('Altitude, km',size=8)
        ax.yaxis.set_label_coords(-0.04,0.5)
        dt = end_time_sec-start_time_sec
        if dt == 3600:
            xtick_pos = [0,600,1200,1800,2400,3000,3600]
        elif dt == 3000:
            xtick_pos = [0,600,1200,1800,2400,3000]
        elif dt == 2400:
            xtick_pos = [0,600,1200,1800,2400]
        elif dt == 1800:
            xtick_pos = [0,300,600,900,1200,1500,1800]
        elif dt == 1200:
            xtick_pos = [0,300,600,900,1200]
        elif dt == 600:
            xtick_pos = [0,120,240,360,480,600]
        else:
            xtick_pos = [0,20,40,60,80,100,120]
        xtick_labels = []
        for t in xtick_pos:
            tt = t + start_time_sec
            if (tt > 3600*24):
                tt = tt - 3600*24
            hour = int(tt/3600)
            minute = int((tt-hour*3600)/60)
            second = int(tt-hour*3600-minute*60)
            xtick_labels.append(("%02d:%02d:%02d") % (hour,minute,second))

        ax.set_xticks(xtick_pos)
        ax.set_xticklabels(xtick_labels)

# Plot histogram of number of sources vs altitutde
def Plot_Hist(ax):
        ax.cla()
        ax.yaxis.set_label_position("right")
        if (len(keep) > 1):
            h,b = np.histogram(state.lma[keep,4],100,(0.0,20000.0))
            b=(b[:-1]+b[1:])/2.0
            ax.plot(h,b/1000.0,'k',linewidth=1.0)
            x1,x2 = ax.get_xlim()
            y1,y2 = ax.get_ylim()
            s = format(len(keep),",d") + " sources"
            #ax.set_ylabel('Altitude, km',size=10)
            x1,x2 = ax.get_xlim()
            if (x2 > 100):
                ax.set_xlim([0,x2])
            else:
                ax.set_xlim([0,100])
            x1,x2 = ax.get_xlim()
            ax.text(x1+(x2-x1)*0.2,y1+(y2-y1)*0.1,s,size=6)
        else:
            ax.set_ylim([0,20.0])
            x1,x2 = ax.get_xlim()
            y1,y2 = ax.get_ylim()
            #ax.set_ylabel('Altitude, km',size=10)
            s = format(len(keep),",d") + " source"
            ax.text(x1+(x2-x1)*0.4,y1+(y2-y1)*0.1,"0 sources",size=6)
            ax.set_xlim([0,100])


if __name__ == '__main__':
    # Let's find out how long it takes to execute
    mystarttime = datetime.datetime.now()
    # Define plotting paramaters
    matplotlib.rcParams['grid.linewidth'] = 0.25
    #matplotlib.rcParams['grid.color'] = '#808080ff'
    matplotlib.rcParams['xtick.direction'] = 'in'
    matplotlib.rcParams['ytick.direction'] = 'in'
    #matplotlib.rcParams['xtick.minor.visible'] = True
    #matplotlib.rcParams['ytick.minor.visible'] = True
    #matplotlib.rcParams['xtick.top'] = True
    #matplotlib.rcParams['ytick.right'] = True
    matplotlib.rcParams['xtick.labelsize'] = 8
    matplotlib.rcParams['ytick.labelsize'] = 8

    if ((len(sys.argv) < 6) or (len(sys.argv) > 7)):
        print(("Usage: %s year month day hour minute [archive_only]\n") % (sys.argv[0]))
        sys.exit(0)
    # If making images for past times, do not want to put these images into the current directory
    if (len(sys.argv) == 7):
        archive_only = True
    else:
        archive_only = False

    # Set up needed paths
    home = os.environ['HOME']
    data_dir = home + '/lma/realtime'
    display_dir = home + '/lma/display'
    # Read configuration file
    conf_file = os.environ['HOME'] + "/lma/lma_config"
    ReadConfFile(conf_file)
    # Find LMA station locations from gps file
    state.network = LmaNetwork()
    fp = open(state.gps_file,"r")
    state.stations = np.empty((0,3))
    for line in fp:
        if line.startswith('#'):
            continue
        elif line.startswith('version'):
            continue
        elif line.startswith('0'):
            ll = line.split()
            state.network.ctr_lng = float(ll[4])
            state.network.ctr_lat = float(ll[3])
        else:
            ll = line.split()
            state.stations = np.append(state.stations,[[float(ll[3]),float(ll[4]),float(ll[5])]],axis=0)


    os.chdir(display_dir)

    # Read map background for plan plots
    if ("mapfile.npz"):
        state.data = np.load("mapfile.npz")
        for key in state.data.keys():
            if (key == "admin0"):
                state.admin0 = state.data['admin0']
            if (key == "admin1"):
                state.admin1 = state.data['admin1']
            if (key == "poi"):
                state.poi = state.data['poi']


    # Find the time for making images.  The time is the last minute of data.  For example, if
    # the time is 13:39, ten-minute files go from 13:30 to 13:40 (13:39 file has data
    # from 13:39:00 to 13:40:00)
    year = int(sys.argv[1])
    if (year < 100):
        year = year + 2000
    month = int(sys.argv[2])
    day = int(sys.argv[3])
    hour = int(sys.argv[4])
    minute = int(sys.argv[5])
    date_str = "%4d/%02d/%02d %02d:%02d:%02d" % (year,month,day,hour,minute,0)
    format_str = "%Y/%m/%d %H:%M:%S"
    end_time = datetime.datetime.strptime(date_str,format_str) + datetime.timedelta(minutes=1)
    # At the end of each 10 minute interval, make the hour images, so need to read
    # enough files to get to the beginning of the last full hour
    if ((minute % 10) == 9):
        min_max = minute + 1
    else:
        min_max = 10
    start_time = end_time-datetime.timedelta(minutes=min_max)
    append = False   # For first file read, will read network info.  For later files, don't re-read
    state.lma = np.empty((0,11))
    for my_minute in range (0,min_max):   # Read last hour of one-minute files
        filetime = start_time + datetime.timedelta(minutes=my_minute)
        fname = home + '/lma/recent/' + state.prefix + "_" + filetime.strftime("%y%m%d_%H%M%S") + "_0060.npy"
        if (os.path.isfile(fname)):
            state.lma = np.append(state.lma,np.load(fname),axis=0)

    rows,cols = state.lma.shape
    g = pyproj.Geod(ellps='WGS84')
    state.geo_min_lng,lat,backaz = g.fwd(state.network.ctr_lng,state.network.ctr_lat,270,400e3)
    state.geo_max_lng,lat,backaz = g.fwd(state.network.ctr_lng,state.network.ctr_lat,90,400e3)
    lng,state.geo_max_lat,backaz = g.fwd(state.network.ctr_lng,state.network.ctr_lat,0,400e3)
    lng,state.geo_min_lat,backaz = g.fwd(state.network.ctr_lng,state.network.ctr_lat,180,400e3)

    # Set up some additional filenames for saving to EOL
    state.do_eol_upload = False
    if state.do_eol_upload:
        eol_basename = "gis.{0}_LMA.%Y%m%d%H%M.{0}_composite".format(state.location)
        state.eol_pngname = end_time.strftime(eol_basename+".png")
        state.eol_kmlname = end_time.strftime(eol_basename+".kml")
        eol_base_url = "https://catalog.eol.ucar.edu/arm_tracer/gis/{0}_lma/%Y%m%d/%H/".format((state.location).lower())
        state.eol_catalogurl = end_time.strftime(eol_base_url + state.eol_pngname)
        state.eol_ftpserver = "catalog.eol.ucar.edu"
        state.eol_ftppath = "/pub/incoming/catalog/tracer"

    # Plot ten minute geo-referenced transparent PNG
    start_time = end_time - datetime.timedelta(minutes=10)
    start_time_sec = start_time.hour*3600 + start_time.minute*60
    end_time_sec = end_time.hour*3600 + end_time.minute*60
    st = calendar.timegm(start_time.utctimetuple())
    state.lma_t = ((state.lma[:,0] - st) + state.lma[:,1])
    if (rows > 1):
        keep, = np.nonzero((state.lma[:,5] > state.lma_limits['min_chi2']) & (state.lma[:,5] < state.lma_limits['max_chi2']) &
             (state.lma[:,4]  > state.lma_limits['min_alt'])  & (state.lma[:,4] < state.lma_limits['max_alt']) &
             (state.lma[:,2]  > state.geo_min_lat)  & (state.lma[:,2]  < state.geo_max_lat)  &
             (state.lma[:,3]  > state.geo_min_lng)  & (state.lma[:,3]  < state.geo_max_lng)  &
             (state.lma[:,7] >= state.lma_limits['min_numsta']) &
             (state.lma_t > 0.0) )
    else:
        keep = []
    # Need these dimensions so plot is 1600 x 1600 pixels
    # The size is about 800 km x 800 km so each pixel is 0.5 km x 0.5 km
    FIGSIZE=(10.323,10.390)
    plt.figure(figsize=FIGSIZE,dpi=400)
    fig,ax_plan = plt.subplots(figsize=FIGSIZE)
    Plot_Geo(ax_plan)
    fin = open("proto_files/GE_realtime.kml","r")
    outname = state.location + "_realtime.kml"
    fout = open(home + "/lma/tmp/" + outname,"w")
    myrand = str(random.randint(1000,9999))
    for line in fin:
        if "LOCATION" in line:
            line = line.replace("LOCATION",state.location)
        if "CTR_LNG" in line:
            line = line.replace("CTR_LNG",str(state.network.ctr_lng))
        if "CTR_LAT" in line:
            line = line.replace("CTR_LAT",str(state.network.ctr_lat))
        if "CBAR_URL" in line:
            line = line.replace("CBAR_URL",str(state.cbar_url) + "?r=" + myrand)
        if "IMAGE_URL" in line:
            line = line.replace("IMAGE_URL",str(state.image_url) + "?r=" + myrand)
        if "NORTH" in line:
            line = line.replace("NORTH",str(state.geo_max_lat))
        if "SOUTH" in line:
            line = line.replace("SOUTH",str(state.geo_min_lat))
        if "EAST" in line:
            line = line.replace("EAST",str(state.geo_max_lng))
        if "WEST" in line:
            line = line.replace("WEST",str(state.geo_min_lng))
        fout.write(line)
    fin.close()
    fout.close()
    shutil.move(home + "/lma/tmp/" + outname,state.www_dir + "/geo_images/" + outname)
    if state.do_eol_upload:
        fin = open("proto_files/GE_realtime.kml","r")
        outname = state.eol_kmlname
        fout = open(home + "/lma/tmp/" + outname,"w")
        myrand = str(random.randint(1000,9999))
        for line in fin:
            if "LOCATION" in line:
                line = line.replace("LOCATION",state.location)
            if "CTR_LNG" in line:
                line = line.replace("CTR_LNG",str(state.network.ctr_lng))
            if "CTR_LAT" in line:
                line = line.replace("CTR_LAT",str(state.network.ctr_lat))
            if "CBAR_URL" in line:
                line = line.replace("CBAR_URL",str(state.cbar_url) + "?r=" + myrand)
            if "IMAGE_URL" in line:
                line = line.replace("IMAGE_URL",str(state.eol_catalogurl) + "?r=" + myrand)
            if "NORTH" in line:
                line = line.replace("NORTH",str(state.geo_max_lat))
            if "SOUTH" in line:
                line = line.replace("SOUTH",str(state.geo_min_lat))
            if "EAST" in line:
                line = line.replace("EAST",str(state.geo_max_lng))
            if "WEST" in line:
                line = line.replace("WEST",str(state.geo_min_lng))
            fout.write(line)
        fin.close()
        fout.close()
        shutil.move(home + "/lma/tmp/" + outname,state.www_dir + "/geo_images/" + outname)
        try:
            # FTP the KML and PNG to EOL
            from ftplib import FTP
            ftp = FTP(state.eol_ftpserver)  # connect to host, default port
            ftp.login()                     # user anonymous, passwd anonymous@
            ftp.cwd(state.eol_ftppath)      # change into "debian" directory
            for filename_send in (outname, state.eol_pngname):
                to_send = open(state.www_dir + "/geo_images/" + filename_send,'rb')
                ftp.storbinary("STOR " + filename_send, to_send)
                to_send.close()
            ftp.quit()
        except:
            print("FTP problem of some sort: ", sys.exc_info()[0])


    # Make plots for different zoom levels
    # Format of a plot_list element is:  zoom; time ('t'), points ('p'), density ('d') or geo_located ('g'); minutes;
    #                                    filename suffix, current ('c'), archive ('r') and/or animation ('a')
    plot_list = []
    if ((minute % 10) == 9):
        plot_list.append((state.z1,'t',10,'_0600_z1_tim','cr','z1'))    # Ten minutes points plot at zoom z1
        plot_list.append((state.z2,'t',10,'_0600_z2_tim','cr','z2'))    # Ten minutes points plot at zoom z2
        plot_list.append((state.z3,'t',10,'_0600_z3_tim','c','z3'))     # Ten minutes points plot at zoom z3
        plot_list.append((state.z1,'d',10,'_0600_z1_den','cra','z1'))   # Ten minutes density plot at zoom z1
        plot_list.append((state.z2,'d',10,'_0600_z2_den','cra','z2'))   # Ten minutes density plot at zoom z2
        plot_list.append((state.z3,'d',10,'_0600_z3_den','ca','z3'))    # Ten minutes density plot at zoom z3
    else:
        plot_list.append((state.z1,'t',10,'_0600_z1_tim','c','z1'))     # Ten minutes points plot at zoom z1
        plot_list.append((state.z2,'t',10,'_0600_z2_tim','c','z2'))     # Ten minutes points plot at zoom z2
        plot_list.append((state.z3,'t',10,'_0600_z3_tim','c','z3'))     # Ten minutes points plot at zoom z3
        plot_list.append((state.z1,'d',10,'_0600_z1_den','ca','z1'))    # Ten minutes density plot at zoom z1
        plot_list.append((state.z2,'d',10,'_0600_z2_den','ca','z2'))    # Ten minutes density plot at zoom z2
        plot_list.append((state.z3,'d',10,'_0600_z3_den','ca','z3'))    # Ten minutes density plot at zoom z3
    plot_list.append((state.z1,'p',2, '_0120_z1_pts','c','z1'))         # Two minutes points plot at zoom z1
    plot_list.append((state.z2,'p',2, '_0120_z2_pts','c','z2'))         # Two minutes points plot at zoom z2
    plot_list.append((state.z3,'p',2, '_0120_z3_pts','c','z3'))         # Two minutes points plot at zoom z3
    plot_list.append((state.z1,'t',2, '_0120_z1_tim','c','z1'))         # Two minutes points plot at zoom z1
    plot_list.append((state.z2,'t',2, '_0120_z2_tim','c','z2'))         # Two minutes points plot at zoom z2
    plot_list.append((state.z3,'t',2, '_0120_z3_tim','c','z3'))         # Two minutes points plot at zoom z3

    make_hour = (((minute % 10) == 9) and (not archive_only)) or (minute == 59)
    if (make_hour):   # At the end of the hour make hourly archive plots
                               # If not at the end of the hour, make plots which contain partial hours
        plot_list.append((state.z1,'t',minute+1,'_3600_z1_tim','r','z1'))  # One hour points plot at z1
        plot_list.append((state.z2,'t',minute+1,'_3600_z2_tim','r','z2'))  # One hour points plot at z2
        plot_list.append((state.z1,'d',minute+1,'_3600_z1_den','r','z1'))  # One hour density plot at z1
        plot_list.append((state.z2,'d',minute+1,'_3600_z2_den','r','z2'))  # One hour density plot at z2

    for p in plot_list:
        # If making old images, skip making image unless they are to be archived
        if ((archive_only) and (not ('r' in p[4]))):
            continue
        if ((p[5] == 'z1') or (p[5] == 'z2') or (p[5] == 'z3')):
            ctr_lat = state.network.ctr_lat
            ctr_lng = state.network.ctr_lng
        else:
            print("Unknown zoom level: " + str(p[5]))
            continue
        pz = p[0]
        pl = p[2]
        start_time = end_time - datetime.timedelta(minutes=pl)
        start_time_sec = start_time.hour*3600 + start_time.minute*60
        end_time_sec = end_time.hour*3600 + end_time.minute*60
        st = calendar.timegm(start_time.utctimetuple())
        state.lma_t = ((state.lma[:,0] - st) + state.lma[:,1])

        state.lma_limits['span'] = pz*1000.0
        min_lat = lma_util.xy2ll(0.0,0.0-pz*1000.0,ctr_lat,ctr_lng)[0]
        max_lat = lma_util.xy2ll(0.0,pz*1000.0,ctr_lat,ctr_lng)[0]
        min_lng = lma_util.xy2ll(0.0-pz*1000.0,0.0,ctr_lat,ctr_lng)[1]
        max_lng = lma_util.xy2ll(pz*1000.0,0.0,ctr_lat,ctr_lng)[1]
        keep = []
        if (rows > 1):
            keep, = np.nonzero((state.lma[:,5] > state.lma_limits['min_chi2']) & (state.lma[:,5] < state.lma_limits['max_chi2']) &
                 (state.lma[:,4]  > state.lma_limits['min_alt'])  & (state.lma[:,4] < state.lma_limits['max_alt']) &
                 (state.lma[:,9]  > (state.lma_limits['centerX'] - state.lma_limits['span']))  &
                 (state.lma[:,9]  < (state.lma_limits['centerX'] + state.lma_limits['span']))  &
                 (state.lma[:,10]  > (state.lma_limits['centerY'] - state.lma_limits['span']))  &
                 (state.lma[:,10]  < (state.lma_limits['centerY'] + state.lma_limits['span']))  &
                 (state.lma[:,7] >= state.lma_limits['min_numsta']) &
                 (state.lma_t > 0.0) )

        # For large images, make six-panel plots
        # Define the subplots
        # Use the following size to get the plan view with 450x450 pixels
        #plt.figure(figsize=(7.93,8.666),facecolor=(245.0/255.0,245.0/255.0,245.0/255.0),dpi=100)
        plt.figure(figsize=(7.93,8.666),dpi=100)
        G = plt.GridSpec(18,5,wspace=0.4,hspace=2.5)
        ax_ta = plt.subplot(G[0:3, :])
        #ax_ta.set_facecolor((245.0/255.0, 245.0/255.0, 245.0/255.0))
        ax_ew = plt.subplot(G[3:6, :-1])
        #ax_ew.set_facecolor((245.0/255.0, 245.0/255.0, 245.0/255.0))
        ax_hist = plt.subplot(G[3:6,4])
        #ax_hist.set_facecolor((245.0/255.0, 245.0/255.0, 245.0/255.0))
        ax_plan = plt.subplot(G[6:, :-1])
        #ax_plan.set_facecolor((245.0/255.0, 245.0/255.0, 245.0/255.0))
        ax_ns = plt.subplot(G[6:, 4])
        #ax_ns.set_facecolor((245.0/255.0, 245.0/255.0, 245.0/255.0))

        Plot_NS(ax_ns,p[1])
        Plot_EW(ax_ew,p[1])
        Plot_TA(ax_ta,p[1])
        Plot_Plan(ax_plan,p[1],'f')
        Plot_Hist(ax_hist)
        my_title = state.location + " LMA " + start_time.strftime("%H%M-") + end_time.strftime("%H%M UTC ") + start_time.strftime("%B %d, %Y")
        ax_ta.set_title(my_title,fontsize=12)

        # Trim whitespace.  Don't use "bbox_inches='tight'" as the plot size will change depending on number
        # of characters in ylabels
        bbox = matplotlib.transforms.Bbox([[0.3, 0.5],[7.6,8.0]])
        temp_name = "/dev/shm/" + next(tempfile._get_candidate_names()) + ".png"
        #plt.savefig(temp_name,bbox_inches=bbox,facecolor=(245.0/255.0,245.0/255.0,245.0/255.0),pad_inches=0.0)
        plt.savefig(temp_name,bbox_inches=bbox,pad_inches=0.0)
        plt.close("all")
        # Draw a border around the image
        bimg_full = ImageOps.expand(Image.open(temp_name),border=4,fill=(192,192,192))
        # The image with border is now in bimg_full.  Get rid of original PNG file
        os.remove(temp_name)

        # If archiving images, make thumbnail
        if ('r' in p[4]):
            # Thumbnails are 1" x 1", with only the plan panel
            #plt.figure(figsize=(1.3,1.3),dpi=100,facecolor=(245.0/255.0,245.0/255.0,245.0/255.0))
            plt.figure(figsize=(1.3,1.3),dpi=100)
            G = plt.GridSpec(1,1,wspace=0.4,hspace=0.3)
            ax_thumb = plt.subplot(G[0, 0])
            Plot_Plan(ax_thumb,p[1],'t')
            ax_thumb.get_xaxis().set_visible(False)
            ax_thumb.get_yaxis().set_visible(False)
            bbox = matplotlib.transforms.Bbox([[0.17, 0.14],[1.18,1.13]])
            temp_name = "/dev/shm/" + next(tempfile._get_candidate_names()) + ".png"
            plt.savefig(temp_name,bbox_inches=bbox)
            plt.close("all")
            # Draw a border around the image
            bimg_thumb = ImageOps.expand(Image.open(temp_name),border=2,fill=(192,192,192))
            # The image with border is now in bimg_thumb.  Get rid of original PNG file
            os.remove(temp_name)

        # Save image(s) in appropriate place(s)
        # Save current image in current directory
        if (('c' in p[4]) and (not archive_only)):
            outdir = state.www_dir + '/current/'
            png_fname = outdir + 'current' + p[3] + ".png"
            bimg_full.save(png_fname)
            print(png_fname)
        # Same animation image in animation diretory
        if (('a' in p[4]) and (not archive_only)):
            if (p[5] == 'z1'):
                outdir = state.www_dir + "/current/anim_z1/"
                outname = state.www_dir + "/current/anim_z1.gif"
            elif (p[5] == 'z2'):
                outdir = state.www_dir + "/current/anim_z2/"
                outname = state.www_dir + "/current/anim_z2.gif"
            elif (p[5] == 'z3'):
                outdir = state.www_dir + "/current/anim_z3/"
                outname = state.www_dir + "/current/anim_z3.gif"
            else:
                print("Unknown zoom level " + str(p[5]))
                continue
            gif_fname = outdir + state.prefix + start_time.strftime("_%y%m%d_%H%M%S") + p[3] + ".gif"
            # Save image as GIF, for making GIF animation
            temp_name = "/dev/shm/" + next(tempfile._get_candidate_names()) + ".png"
            bimg_full.save(temp_name)
            cmd = "convert " + temp_name+ " " + gif_fname
            print(cmd)
            sp.call(cmd,shell=True)
            os.remove(temp_name)
            # Now make animation from images.  Pause 10 ms between images, and 250 ms after last image
            myfiles = sorted(glob.glob(outdir + "*gif"))
            filelist = " "
            for item in myfiles[-state.anim_len:]:
                filelist = filelist + item + " "
            cmd = "convert -loop 0 -delay 20 " + filelist + " -delay 250 " + gif_fname + " " + outname
            #print(cmd)
            sp.call(cmd,shell=True)
            # Delete older files in image directory
            myfiles = sorted(glob.glob(outdir + "*gif"))
            for item in myfiles[:-state.anim_len]:
                os.remove(item)
        # If archiving images, save in the "/img" subdirectory
        if ('r' in p[4]):
            outdir = state.www_dir + '/img/' + start_time.strftime("%y/%m/%d/%H")
            mkdir_p(outdir)
            fname = outdir + "/" + state.prefix + start_time.strftime("_%y%m%d_%H%M%S") + p[3] + ".full.png"
            bimg_full.save(fname)
            print(fname)
            fname = outdir + "/" + state.prefix + start_time.strftime("_%y%m%d_%H%M%S") + p[3] + ".thumb.png"
            bimg_thumb.save(fname)
            print(fname)

    # Print execution time
    print(datetime.datetime.now() - mystarttime)
