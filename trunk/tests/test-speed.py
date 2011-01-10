import gps
import sys
import os
import time

session = gps.gps()

while 1:
	session.query('admosyi')
	os.system("clear")
	print session.fix.speed, "raw"
	print session.fix.speed, "m/s"
	print session.fix.speed * 3.6, "kph"
	print session.fix.speed * 2.237, "mph"
	time.sleep(0.1)
