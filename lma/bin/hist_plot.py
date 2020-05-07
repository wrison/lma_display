#!/usr/bin/python
from matplotlib import rc
import matplotlib
matplotlib.use('Agg')
import pylab
import matplotlib.pyplot as plt
import numpy as np
import sys
import string
import gzip
import time
from datetime import date
import os.path
import os
import multiprocessing as mp
import subprocess as sp
import glob
import shutil

rc('text', usetex=False)
rc('font', family='sans-serif')
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

fp = open(os.environ['HOME'] + '/lma/lma_config')
for line in fp:
    if (line.startswith('www_dir:')):
        www_dir = line.split()[1]
fp.close()
plots_dir = www_dir + "/plots/"  # Where the plots go
log_dir = os.environ['HOME'] + '/lma/log/'

for line in glob.glob(log_dir + "T*"):
	fname = line.split('/')[-1]
	letter = fname[1]
	shutil.move(log_dir + fname, log_dir + letter + "/" + fname)

station = {}
station_letters = []
fid = open(www_dir + "/stations.txt","r")
for line in fid:
    letter = line.split()[0]
    if (len(letter) == 1):
        name = line[2:].rstrip()
        station[letter] = name
fid.close()

if (len(sys.argv) == 2):
	datestring = sys.argv[1]
	year = datestring[0:2];
	month = datestring[2:4];
	mday = datestring[4:6];
	datestringprint = "20"+year+"/"+month+"/"+mday;
else:
	today = date.today()
	datestring = today.strftime("%y%m%d")
	datestringprint = today.strftime("%Y/%m/%d")
for st_letter,st_name in station.iteritems():
    basename = 'T' + st_letter + datestring
    filename = log_dir + st_letter + '/' + basename + '.gz'
    print(filename)
    if (os.path.isfile(filename)):
        fp = gzip.open(filename,'rb')
        line = fp.readline()
        linelist = string.split(line)
        t = []
        t.append((float(line[11:13])*3600 + float(line[14:16])*60 + float(line[17:19]))/3600.0);
        thresh_pos = 4;
        if (len(linelist) == 13):
            sat_pos = 7
            temp_pos = 9
            trig_pos = 6
        else:
            sat_pos = 8
            temp_pos= 10
            trig_pos = 7
        thresh = [int(linelist[thresh_pos],16)]
        sat= [int(linelist[sat_pos])]
        temp= [int(linelist[temp_pos][:-1])]
        trig = [int(linelist[trig_pos])]
        line = fp.readline()
        has_volts = 0
        while (line):
            if (line.find("voltage") > 0):
                has_volts = 1
                break
            t.append((float(line[11:13])*3600 + float(line[14:16])*60 + float(line[17:19]))/3600.0);
            linelist = string.split(line)
            if (len(linelist) == 13):
                sat_pos = 7
                temp_pos = 9
                trig_pos = 6
            else:
                sat_pos = 8
                temp_pos= 10
                trig_pos = 7
            thresh.append(int(linelist[thresh_pos],16))
            sat.append(int(linelist[sat_pos]))
            temp.append(int(linelist[temp_pos][:-1]))
            trig.append(int(linelist[trig_pos]))
            line = fp.readline()
        
        thresh_dB = np.array(thresh,dtype='double') * 0.488 - 111.0;
                
        if (has_volts == 1):
            tv = []
            tv.append((float(line[11:13])*3600 + float(line[14:16])*60 + float(line[17:19]))/3600.0);
            linelist = string.split(line)
            lv= [float(linelist[9])]
            b2v = [float(linelist[13])]
            b1v = [float(linelist[21])]
            lc= [float(linelist[29])]
            b2c = [float(linelist[33])]
            b1c = [float(linelist[41])]
            line = fp.readline()
            while (line):
                tv.append((float(line[11:13])*3600 + float(line[14:16])*60 + float(line[17:19]))/3600.0);
                linelist = string.split(line)
                lv.append(float(linelist[9]))
                b2v.append(float(linelist[13]))
                b1v.append(float(linelist[21]))
                lc.append(float(linelist[29]))
                b2c.append(float(linelist[33]))
                b1c.append(float(linelist[41]))
                line = fp.readline()
            
        if (has_volts == 1):
            fig, ((ax1, ax2, ax3, ax4, ax5, ax6)) = plt.subplots(nrows=6, ncols=1,figsize=(8,8))
        else:
            fig, ((ax1, ax2, ax3, ax4)) = plt.subplots(nrows=4, ncols=1)

        ax1.plot(t,thresh_dB)
        ax1.set_title(st_name + '               Threshold                    ' + datestringprint)
        ax1.axis([0, 24, -100, -50])
        ax1.grid(True)
        ax1.set_yticks([-100, -90, -80, -70, -60, -50])
        ax1.set_xticks([0, 4, 8, 12, 16, 20, 24])
        ax1.set_ylabel('dBm')
        
        ax2.plot(t,trig)
        ax2.set_title('Triggers/sec')
        ax2.axis([0, 24, 0, 12500])
        ax2.grid(True)
        ax2.set_yticks([0, 4000, 8000, 12000])
        ax2.set_xticks([0, 4, 8, 12, 16, 20, 24])
        ax2.set_ylabel('Count')
        
        ax3.plot(t,temp)
        ax3.set_title('Temperature')
        ax3.axis([0, 24, -20, 80])
        ax3.grid(True)
        ax3.set_yticks([-20, 0, 20, 40, 60, 80])
        ax3.set_xticks([0, 4, 8, 12, 16, 20, 24])
        ax3.set_ylabel(r'$^o$C')
        
        ax4.plot(t,sat)
        ax4.set_title('Satellites Tracked')
        ax4.axis([0, 24, 0, 12])
        ax4.grid(True)
        ax4.set_xticks([0, 4, 8, 12, 16, 20, 24])
        ax4.set_yticks([0, 4, 8, 12])
        ax4.set_ylabel('Number')

        if (has_volts):
            ax5.plot( tv, b1v, tv, b2v, tv, lv )
            t1 = [2.5,3.5]
            l1 = [14.8, 14.8]
            ax5.plot(t1,l1,'blue')
            t1 = [6.5,7.5]
            l1 = [14.8, 14.8]
            ax5.plot(t1,l1,'green')
            t1 = [10.5,11.5]
            l1 = [14.8, 14.8]
            ax5.plot(t1,l1,'red')
            ax5.set_title('Voltages')
            ax5.axis([0, 24, 10, 16])
            ax5.grid(True)
            ax5.set_xticks([0, 4, 8, 12, 16, 20, 24])
            ax5.set_yticks([10, 12, 14, 16])
            ax5.text(1,14.5,'Batt1',color='blue')
            ax5.text(5,14.5,'Batt2',color='green')
            ax5.text(9,14.5,'Load',color='red')
            ax5.set_ylabel('Volts')


            ax6.plot( tv, b1c, tv, b2c, tv, lc)
            t1 = [2.5,3.5]
            l1 = [3, 3]
            ax6.plot(t1,l1,'blue')
            t1 = [6.5,7.5]
            l1 = [3, 3]
            ax6.plot(t1,l1,'green')
            t1 = [10.5,11.5]
            l1 = [3, 3]
            ax6.plot(t1,l1,'red')
            ax6.set_title('Currents')
            ax6.axis([0, 24, -2, 4])
            ax6.grid(True)
            ax6.set_xticks([0, 4, 8, 12, 16, 20, 24])
            ax6.set_yticks([-2, 0, 2, 4])
            ax6.text(1,2.7,'Batt1',color='blue')
            ax6.text(5,2.7,'Batt2',color='green')
            ax6.text(9,2.7,'Load',color='red')
            ax6.set_ylabel('Amps')
            
           
 
        outname = plots_dir + st_letter + '/' +basename + '.png'
        print(outname)
        plt.tight_layout()
        #plt.show()
        plt.savefig(outname)
