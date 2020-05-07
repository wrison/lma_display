#!/usr/bin/env python
import pyproj
import numpy as np
import os
import gzip
import sys
import shapefile as shp

def extract_shapefile(shapefile):
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
                for item in x:
                    lng.append(item)
                lng.append(float("NaN"))
                for item in y:
                    lat.append(item)
                lat.append(float("NaN"))
                #axis.plot(x,y,color=clr,zorder=order,linewidth=lw)
        except:
            pass
    

def extract_datfile(datfile):
    fid = open(datfile,"r")
    stop = False
    for line in fid:
        ll = line.split()
        if (len(ll)==3):
            continue
        if ((line.startswith("END")) and stop):
            break
        if ((line.startswith("END")) and not stop):
            lat.append(float("NaN"))
            lng.append(float("NaN"))
            stop = True
        if (len(ll) == 2):
            lat.append(float(ll[1]))
            lng.append(float(ll[0]))
            stop = False

def extract_poi(txtfile):
    fid = open(txtfile)
    for line in fid:
        if (line.startswith("#")):
            continue
        lat.append(float(line.split()[1]))
        lng.append(float(line.split()[2]))
    
lng = []
lat = []
extract_shapefile("maps/states.shp")
lnga = np.asarray(lng)
lata = np.asarray(lat)
admin0 = np.vstack((np.asarray(lat),np.asarray(lng))).T

lng = []
lat = []

extract_datfile("maps/counties/UT.dat")
extract_datfile("maps/counties/WY.dat")
extract_datfile("maps/counties/AZ.dat")
extract_datfile("maps/counties/NV.dat")

lnga = np.asarray(lng)
lata = np.asarray(lat)
admin1 = np.vstack((np.asarray(lat),np.asarray(lng))).T

lng = []
lat = []
extract_poi("maps/poi.txt")
lnga = np.asarray(lng)
lata = np.asarray(lat)
poi = np.vstack((np.asarray(lat),np.asarray(lng))).T



np.savez("mapfile.npz",admin0=admin0,admin1=admin1,poi=poi)
