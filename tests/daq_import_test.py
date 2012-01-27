#!/usr/bin/env python

import daq, time

try:
	daq.ping()
       	print "DACQ is present"
        daq = 7
except IOError: 
	pass
        print "DACQ not present"
        daq = 0
	time.sleep(5)
        sys.exit()

response = daq.ping()
print "Ping? :", response

print "All channels :", daq.all()

print "One channel :", daq.one(5)

print "w3str is", w3str
print "daq is", daq
