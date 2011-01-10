#!/usr/bin/env python

import time,serial,sys,os

INTERVAL = 1.0            # seconds between samples
DLP_DEV = "/dev/serial/by-id/usb-DLP_Design_DLP-IO8_DP123456-if00-port0"

# DLP-IO8-G codes, ports 1 - 8
DO_HI = ['1','2','3','4','5','6','7','8'] # set dig out high
DO_LO = ['Q','W','E','R','T','Y','U','I'] # set dig out low
DI    = ['A','S','D','F','G','H','J','K'] # read dig in
AI    = ['Z','X','C','V','B','N','M',','] # read analog in
TI    = ['9','0','-','=','O','P','[',']'] # read temp in
DLPASC= '`' # set ascii mode
DLPBIN= '\\' # set binary mode
DLPF  = 'L' # set fahrenheit
DLPC  = ';' # set celsius
DLPING= "'" # ping

T_RETRY= 2.0            # wait time if retrying. (exptl)
NTRY=1                  # Number of retries allowed for temps.
T0 = 0.002                # spacing between temp. commands (exptl)
T1 = 0.002                # spacing between channels (exptl)

state = [0,0,0,0,0,0,0,0]

def dio_decode(raw, id):
    # check to see if the [list] contains whatever is in raw
    if not raw in [chr(0), chr(1)]:
        # it does not...
        print "ulog: invalid digital input [%s]: %d" \
            % (id, ord(raw))
	   # ... so return chr(0) == ASCII 0x00, NUL, whatever you want to call it
        raw = chr(0)
    # returns the inverse of raw	
    # return 1 - ord(raw)
    # return the normal raw
    return ord(raw)

def ping():
        # Open DLP-IO8-G device which appears as DLP_DEV
        # Assume we have appropriate privilege.
        try:
                ser = serial.Serial(DLP_DEV, 115200, timeout=1)
        except serial.serialutil.SerialException:
                # print "ulog: Can't open DLP-IO8-G on %s, terminating." % DLP_DEV
		print "Can't open DLP-IO8-G on %s" % DLP_DEV
                # sys.exit() ## Comment out by KG. We really should return a failure instead
		return 0 #FIXME

        ser.write(DLPBIN)        # ensure binary mode

        try:
		#print "Testing channel :", channel, "with command :", AI[channel]
			for i in range(NTRY):    # Allow retries in case of blown reading
				ser.write(DLPING) # Ping it
				#time.sleep(T0)    # slowdown -> more reliable?
				raw = ser.read(1)
				#print "Raw is :", ord(raw)
				#state[channel] = dio_decode(raw, "Channel " + str(channel))
				if raw == "Q":
					state = 1
				else:
					state = 0
				#print "State :", state

        except KeyboardInterrupt:        # e.g., from kill -SIGINT <proc>
                pass                # graceful termination

        # Close up files and terminate.
        ser.close()
        return state

def all():
	# Open DLP-IO8-G device which appears as DLP_DEV
	# Assume we have appropriate privilege.
	try:
		ser = serial.Serial(DLP_DEV, 115200, timeout=1)
	except serial.serialutil.SerialException:
		print "ulog: Can't open DLP-IO8-G on %s, terminating." % DLP_DEV
		sys.exit()

	ser.write(DLPBIN)        # ensure binary mode

	try:
		for channel in range(8):
			#print "Testing channel :", channel, "with command :", AI[channel]
			for i in range(NTRY):    # Allow retries in case of blown reading
				ser.write(DI[channel]) # Digital input
				#time.sleep(T0)    # slowdown -> more reliable?
				raw = ser.read(1)
				#print "Raw is :", ord(raw)
				state[channel] = dio_decode(raw, "Channel " + str(channel))
				#print "State :", state[channel]
		#print state

	except KeyboardInterrupt:        # e.g., from kill -SIGINT <proc>
		pass                # graceful termination

	# Close up files and terminate.
	ser.close()
	return state

def one(channel):
        # Open DLP-IO8-G device which appears as DLP_DEV
        # Assume we have appropriate privilege.
        try:
                ser = serial.Serial(DLP_DEV, 115200, timeout=1)
        except serial.serialutil.SerialException:
                print "ulog: Can't open DLP-IO8-G on %s, terminating." % DLP_DEV
                sys.exit()

        ser.write(DLPBIN)        # ensure binary mode

        try:
		#print "Testing channel :", channel, "with command :", AI[channel]
		for i in range(NTRY):    # Allow retries in case of blown reading
			ser.write(DI[channel]) # Digital input
			#time.sleep(T0)    # slowdown -> more reliable?
			raw = ser.read(1)
			#print "Raw is :", ord(raw)
			state[channel] = dio_decode(raw, "Channel " + str(channel))
			#print "State :", state[channel]

        except KeyboardInterrupt:        # e.g., from kill -SIGINT <proc>
                pass                # graceful termination

        # Close up files and terminate.
        ser.close()
	return state[channel]

