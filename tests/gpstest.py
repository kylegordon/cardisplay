#!/usr/bin/env python2.5
from gps import *
(host, port, device) = ("localhost", "2947", None)
debug=0
try:
    daemon = gps(host=host,
            port=port,
            mode=WATCH_ENABLE|WATCH_JSON|WATCH_SCALED,
            verbose=debug)
    while (True):
        # Do stuff
        if daemon.poll() == -1:
            print "daemon error"
        if daemon.valid & PACKET_SET:
            report = daemon.data
            # if (0==1):
            print report

	    print daemon.fix.speed
	    print "Mode is " + str(daemon.fix.mode)
except socket.error:
    print "GPSD not running"

