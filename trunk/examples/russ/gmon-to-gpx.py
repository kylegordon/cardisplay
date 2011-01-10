#!/usr/bin/python

import sys, os, re, stat, time

#BSSID;LAT;LON;SSID;Crypt;Beacon Interval;Connection Mode;Channel;RXL;Date;Time
#00:12:17:46:61:29;44.72952;-74.94478;Crynwr;Open;AAA;Infra;1;-76;2009/12/27;14:59:00
#00:02:A8:AD:CB:0D;44.66837;-74.98721;myLGNet;Wep;AAA;Infra;1;-83;2009/12/21;16:33:08
#00:00:00:F1:F1:F1;44.72952;-74.94478;04Z412558730;Wep;AAA;Infra;6;-75;2009/12/27;15:32:18
#00:0E:9B:3E:8A:CF;44.72952;-74.94478;a95b;Wep;AAA;Infra;6;-85;2009/12/26;16:28:42

    
model = [
"""<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.1"
  creator="makegpx"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/1"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<metadata>
    <time>%s</time>
</metadata>
""","""  <wpt lat="%s" lon="%s"><desc>%s</desc></wpt>
""","""</gpx>
"""]
    
def convertone(fn, outfn):
    
    waypoints = []
    inf = open(fn)
    outf = open(outfn, "w")
    mtime = os.stat(fn)[stat.ST_MTIME]
    filetime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(mtime))
    outf.write(model[0] % filetime)
    for line in inf:
        fields = line.split(";")
        if fields[0] == " BSSID":
            continue
#BSSID;LAT;LON;SSID;Crypt;Beacon Interval;Connection Mode;Channel;RXL;Date;Time
#00:0E:9B:3E:8A:CF;44.72952;-74.94478;a95b;Wep;AAA;Infra;6;-85;2009/12/26;16:28:42
        lat = fields[1]
        lon = fields[2]
        trkptdate = "%s-%s-%sT%sZ" % (fields[9][0:4],fields[9][5:7],fields[9][8:10],fields[10])
        outf.write(model[1] % (lat, lon, fields[3]))
    outf.write(model[2])
    
for fn in sys.argv[1:]:
    print fn
    convertone(fn, fn+".gpx")

