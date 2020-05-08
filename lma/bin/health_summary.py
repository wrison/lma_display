#!/usr/bin/python
import collections
import os
import time
import multiprocessing as mp
import subprocess as sp
import sys

# Parse the station health data -- Bill Rison <rison@lmatechnologies.com>
# 5/30/17: First written, adapted from Perl code by Tim Hamlin

fp = open(os.environ['HOME'] + '/lma/lma_config')
for line in fp:
    if (line.startswith('www_dir:')):
        www_dir = line.split()[1]
    if (line.startswith('Location:')):
        location = line.split()[1]
    if (line.startswith('station_id:')):
        station_id = line.split()[1]
fp.close()
status_dir = os.environ['HOME'] + "/lma/status" 
status_file = www_dir + "/status.html"

stations = collections.OrderedDict()
station_letters = []
fp = open(www_dir + "/stations.txt","r")
for line in fp:
    letter = line.split()[0].lower()
    if (len(letter) == 1):
        k = station_id + letter
        stations[k] = {}
        stations[k]["station"] = k
        stations[k]["name"] = line[2:].rstrip()
        station_letters.append(letter)
fp.close()

fp_out = open(status_file,"w")

# Read new station status files
for k, v in stations.items():
    if (os.path.isfile(status_dir + "/" + k)):
        fp = open(status_dir + "/" + k,"r")
        for line in fp:
            if (len(line) < 3):
                continue
            innerkey = line.split()[0]
            innerval = line[len(innerkey)+1:].rstrip()
            stations[k][innerkey] = innerval
        fp.close()
        os.rename(status_dir + "/" + k,status_dir + "/" + k + "_old")
    elif (os.path.isfile(status_dir + "/" + k + "_old")):
        stations[k]["status"] = "down"
        fp = open(status_dir + "/" + k + "_old","r")
        for line in fp:
            if (len(line) < 3):
                continue
            if (line.split()[0] == "station"):
                stations[k]["station"] = line[len("station")+1:].rstrip()
            if (line.split()[0] == "name"):
                stations[k]["name"] = line[len("name")+1:].rstrip()
            if (line.split()[0] == "sdate"):
                stations[k]["sdate"] = line[len("sdate")+1:].rstrip()
            if (line.split()[0] == "stime"):
                stations[k]["stime"] = line[len("stime")+1:].rstrip()
        fp.close()
    else:
        stations[k]["status"] = '<font color="red">offline</font>'

# Status file header information
fp_out.write("<html>\n\n<head>\n\t<META HTTP-EQUIV=\"refresh\" content=\"60;URL=status.html\">\n\t<title> " + location + " LMA Status</title>\n</head>\n\n<body>\n")
fp_out.write("<html>\n\n<head>\n\t<META HTTP-EQUIV=\"refresh\" content=\"60;URL=status.html\">\n\t<title> " + location + " LMA Status</title>\n</head>\n\n<body>\n")
fp_out.write("\t<h2> " + location + " Lightning Mapping Array, Station Health Data \t&nbsp;&nbsp;&nbsp;<a href=stat_plots.php?station=A>Status Plots</a></h2>\n")
now = time.asctime(time.gmtime())
fp_out.write("\t<em>(information updated hourly, at twenty past -- last updated: " + now + " UTC)</em>\n")

html = {"station" : "\t\t\t<th><a href=\"desc.html#station\">station</a></th>"}
html["name"] = "\t\t\t<th><a href=\"desc.html#name\">name</a></th>";
html["status"] = "\t\t\t<th><a href=\"desc.html#status\">status</a></th>";
html["sdate"] = "\t\t\t<th><a href=\"desc.html#sdate\">sdate</a></th>";
html["stime"] = "\t\t\t<th><a href=\"desc.html#stime\">stime</a></th>";
html["load"] = "\t\t\t<th><a href=\"desc.html#load\">load</a></th>";
html["uptime"] = "\t\t\t<th><a href=\"desc.html#uptime\">uptime</a></th>";
html["duty"] = "\t\t\t<th><a href=\"desc.html#duty\">duty</a></th>\n";
html["slash"] = "\t\t\t<th><a href=\"desc.html#slash\">/</a></th>";
html["boot"] = "\t\t\t<th><a href=\"desc.html#boot\">boot</a></th>";
html["shm"] = "\t\t\t<th><a href=\"desc.html#shm\">/dev/shm</a></th>";
html["data"] = "\t\t\t<th><a href=\"desc.html#data\">/data</a></th>";
html["pid"] = "\t\t\t<th><a href=\"desc.html#pid\">PID</a></th>";
html["pidrd"] = "\t\t\t<th><a href=\"desc.html#pidrd\">PIDRD</a></th>";
html["pidtl"] = "\t\t\t<th><a href=\"desc.html#pidtl\">PIDTL</a></th>";
html["pidat"] = "\t\t\t<th><a href=\"desc.html#pidat\">PIDAT</a></th>";
html["piddec"] = "\t\t\t<th><a href=\"desc.html#piddec\">PIDDEC</a></th>";
html["pphase"] = "\t\t\t<th><a href=\"desc.html#pphase\">Phase</a></th>";
html["pdate"] = "\t\t\t<th><a href=\"desc.html#pdate\">pdate</a></th>";
html["ptime"] = "\t\t\t<th><a href=\"desc.html#ptime\">ptime</a></th>";
html["temp"] = "\t\t\t<th><a href=\"desc.html#temp\">temp</a></th>";
html["gps"] = "\t\t\t<th><a href=\"desc.html#gps\">gps</a></th>";
html["ctrig"] = "\t\t\t<th><a href=\"desc.html#ctrig\">current trigfile</a></th>";
html["trigid"] = "\t\t\t<th><a href=\"desc.html#trigid\">trig ID</a></th>";
html["tdate"] = "\t\t\t<th><a href=\"desc.html#tdate\">tdate</a></th>";
html["ttime"] = "\t\t\t<th><a href=\"desc.html#ttime\">ttime</a></th>";
html["tver"] = "\t\t\t<th><a href=\"desc.html#tver\">tver</a></th>";
html["tthresh"] = "\t\t\t<th><a href=\"desc.html#tthresh\">tthresh</a></th>";
html["ttrigs"] = "\t\t\t<th><a href=\"desc.html#ttrigs\">ttrigs/s</a></th>";
html["tsat"] = "\t\t\t<th><a href=\"desc.html#tsat\">tsat</a></th>";
html["ttemp"] = "\t\t\t<th><a href=\"desc.html#ttemp\">ttemp</a></th>";
html["curr_data_file"] = "\t\t\t<th><a href=\"desc.html#curr_data_file\">current datafile</a></th>";
html["datafile"] = "\t\t\t<th><a href=\"desc.html#datafile\">current datafile</a></th>";
html["fl0"] = "\t\t\t<th><a href=\"desc.html#fl0\">files today</a></th>";
html["fl1"] = "\t\t\t<th><a href=\"desc.html#fl1\">files today-1</a></th>";
html["fl2"] = "\t\t\t<th><a href=\"desc.html#fl2\">files today-2</a></th>";
html["vp1"] = "\t\t\t<th><a href=\"desc.html#fl2\">vp1</a></th>";
html["cp1"] = "\t\t\t<th><a href=\"desc.html#fl2\">cp1</a></th>";
html["vb1"] = "\t\t\t<th><a href=\"desc.html#fl2\">vb1</a></th>";
html["cb1"] = "\t\t\t<th><a href=\"desc.html#fl2\">cb1</a></th>";
html["vl"] = "\t\t\t<th><a href=\"desc.html#fl2\">vl</a></th>";
html["cl"] = "\t\t\t<th><a href=\"desc.html#fl2\">cl</a></th>";
html["rtb"] = "\t\t\t<th><a href=\"desc.html#rtb\">bytes/month</a></th>";
html["rtt"] = "\t\t\t<th><a href=\"desc.html#rtt\">decimation status</a></th>";

# Upper part of status page
fp_out.write("\t<table border>\n")

# Items in upper part of status table
keys = [ "station", "name", "status", "sdate", "stime", "load", "uptime", "duty", "slash", "boot", "shm", "data", "pid", "pidrd", "pidtl", "pidat", "piddec", "pphase", "pdate", "ptime", "temp", "gps", "ctrig" ]

for key in keys:
    fp_out.write(html[key] + "\n")
fp_out.write("\t\t</tr>\n\n")

for k in stations:
    for key in keys:
        try:
            fp_out.write("\t\t\t<td>" +  stations[k][key] + "</td>\n")
        except:
            fp_out.write("\t\t\t<td>---</td>\n")
    fp_out.write("\t\t</tr>\n\n")

fp_out.write("\t</table>\n\n")
fp_out.write("\n<br><p>\n\n")

# Lower part of status page
        
fp_out.write("\t<table border>\n")

# Items in lower part of status table
keys = [ "station", "trigid", "tdate", "ttime", "tver", "tthresh", "ttrigs", "tsat", "ttemp", "fl0", "fl1", "fl2", "datafile", "vp1", "cp1", "vb1", "cb1","vl","cl", "rtb", "rtt" ]

for key in keys:
    fp_out.write(html[key] + "\n")
fp_out.write("\t\t</tr>\n\n")

for k in stations:
    for key in keys:
        try:
            fp_out.write("\t\t\t<td>" +  stations[k][key] + "</td>\n")
        except:
            fp_out.write("\t\t\t<td>---</td>\n")
    fp_out.write("\t\t</tr>\n\n")

fp_out.write("\t</table>\n\n")
fp_out.write("\n<br>\n\n")

