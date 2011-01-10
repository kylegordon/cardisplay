#!/usr/bin/python

# Testing GPX model output
# Fuck knows if this works

import sys


## GPX model

# Header, metadata, tracks, track segments, waypoints (with descriptions)
model = [
"""<gpx
  version="1.1"
  creator="makegpx"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/1"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">""",
  """  <metadata>
    <time>%s</time>
  </metadata>""",
  """  <trk>""",
  """    <trkseg>""",
  """      <trkpt lat="%s" lon="%s"><time>%s</time></trkpt>""",
  """      <trkpt lat="%s" lon="%s"><desc>%s</desc><time>%s</time></trkpt>""",
  """    </trkseg>""",
  """  </trk>""",
  """  <wpt>
    <desc>%s</desc>
  </wpt>""",
  """</gpx>"""]

# Set up some easy refs for portions
# Seems like a shit way of doing it. Must be easier...

gpxheader=0
metadata=1
trkstart=2
trksegstart=3
trkpt=4
trkptdesc=5
trksegend=6
trkend=7
wpt=8
gpxend=9

# Dump some of it out to see if it works - at all

lat = 10
lon = 20
time = 30
desc = "some text"

print model[gpxheader]
print model[metadata] % (time)
print model[trkstart]
print model[trksegstart]
print model[trkpt] % (lat, lon, time)
print model[trkptdesc] % (lat, lon, time, desc)
print model[trksegend]
print model[trkend]
print model[wpt] % (desc)
print model[gpxend]


# sys.stdout.write(model[0])

