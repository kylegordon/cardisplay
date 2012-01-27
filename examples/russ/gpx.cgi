#!/usr/bin/python

import sys, os, re, string, stat, time

fn = sys.argv[1]

if os.environ.has_key("HTTP_HOST"):
    print "Content-Type: application/gpx\nContent-Disposition: attachment; filename=%s\n" % fn

"""
  <metadata>
    <name>%s</name>
    <copyright>Copyright 2005 Russell Nelson nelson@crynwr.com</copyright>
  </metadata>
"""

model = [
"""<gpx
  version="1.1"
  creator="http://rutlandtrail.org/gpx.cgi">
  <trk>
""","""    <trkseg>
""","""      <trkpt lat="%s" lon="%s"><time>%s</time></trkpt>
""","""      <trkpt lat="%s" lon="%s"><desc>%s</desc><time>%s</time></trkpt>
""","""    </trkseg>
""","""  </trk>
</gpx>
"""]

sys.stdout.write(model[0])
infn = os.path.join("data",fn)
inf = open(infn)
mtime = os.stat(infn)[stat.ST_MTIME]
filetime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(mtime))
sys.stdout.write(model[1])
lines = inf.readlines()
for lineno in xrange(len(lines)):
    line = lines[lineno]
    fields = string.split(line)
    if fields[0] == 'TRK':
        lastlatlon = fields[1:3]
        if len(fields) <4:
            sys.stdout.write(model[2] % (fields[1], fields[2], filetime))
        else:
            desc = fields[3].replace('&', '&amp;')
            sys.stdout.write(model[3] % (lastlatlon[0], lastlatlon[1], desc, filetime))
    elif fields[0] == 'STR':
        fields = string.split(line, 1)
        sys.stdout.write(model[3] % (lastlatlon[0], lastlatlon[1], fields[1], filetime))
    elif fields[0] == 'ATTR':
        sys.stdout.write(model[4])
        sys.stdout.write(model[1])
        sys.stdout.write(model[2] % (lastlatlon[0], lastlatlon[1]))
    elif fields[0] == 'TRKI':
        sys.stdout.write(model[4])
        sys.stdout.write(model[1])
sys.stdout.write(model[4])
sys.stdout.write(model[5])

