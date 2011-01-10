#!/usr/bin/python -tt
# -*- coding: iso-8859-1 -*-

import sys,os,time,array
import pylcd

p=pylcd.client()
print 'Connect message:', p.connect()
print 'Info as know by the module:'
p.getinfo()
print 'Setting some info to the display.'

(sysname, nodename, release, version, machine)=os.uname()

#Define some screens
Main='main'
Screen2='Screen2'

#Define some widgets
w1='w1'
w2='w2'
w3='w3'
w4='w4'

#Bargraph testing
#p.screen_add(Main)
#p.screen_set(Main,"-backlight blink")
#p.widget_add(Main,w1,'hbar')
#p.widget_add(Main,w2,'hbar')

#Bignum testing
mphspeed=0
p.screen_add(Main)
p.screen_set(Main,"-priority info")
p.screen_set(Main,"-heartbeat off")
p.widget_add(Main,w1,'num')
p.widget_add(Main,w2,'num')

for i in range(10, 100):
	time.sleep(0.005)
	mphspeed=str(i)	
	p.widget_set(Main,w1,'1 "' + mphspeed[0] + '"')
	p.widget_set(Main,w2,'6 "' + mphspeed[1] + '"')
else:
	print "End of loop"

p.screen_add(Screen2)
p.screen_set(Screen2,"-priority background")
p.widget_add(Screen2,w1,'string')
p.widget_set(Screen2,w1,'1 1 "This is screen 2"')

p.screen_set(Main,"-priority info")
p.screen_set(Screen2,"-priority background")
print "Main has info and Screen2 has background"
time.sleep(5)

p.screen_set(Screen2,"-priority info")
p.screen_set(Main,"-priority background")
print "Main has background and Screen2 has info"
time.sleep(5)

p.screen_set(Main,"-priority info")
p.screen_set(Screen2,"-priority background")
print "Main has info and Screen2 has background"
time.sleep(5)

p.screen_set(Screen2,"-priority info")
p.screen_set(Main,"-priority background")
print "Main has background and Screen2 has info"

#for i in range(0, 100):
#	time.sleep(0.005)
#	p.widget_set(Main,w1,"1 2 " + str(i))
#        p.widget_set(Main,w2,"1 3 " + str(i))
#else:
#	print "End of loop"

## What comes below is individual line tests
#p.screen_add(Main)
#p.widget_add(Main,w1,'string')
#p.widget_add(Main,w2,'string')
#p.widget_add(Main,w3,'string')
#p.widget_add(Main,w4,'string')

#p.widget_set(Main,w1,'1 1 "Line 1"')
#p.widget_set(Main,w2,'1 2 "Line 2"')
#p.widget_set(Main,w3,'1 3 "äöüß"')
#p.widget_set(Main,w4,'1 4 "Line 4"')

#p.screen_add(Screen2)
#p.widget_add(Screen2,w1,'string')
#p.widget_add(Screen2,w2,'string')
#p.widget_add(Screen2,w3,'string')
#p.widget_add(Screen2,w4,'string')

#p.widget_set(Screen2,w1,'1 1 "Line 1, Screen 2"')


print 'All done.'

try:
    raw_input('Press a key to continue')
except EOFError:
    print '\nEOF'

print 'Exit.'

