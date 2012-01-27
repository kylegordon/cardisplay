#!/usr/bin/env python
# $Id$

"""
LCDproc client showing RAID and Nagios status on a CrystalFontz 635 display.
This client is a combination of lcdmdstat and lcdnag, reason being that the
CrystalFontz 635 LEDs are updated by both clients causing a flickering effect.
By combining them into one, the LEDs are updated properly.

Limitations:
o first of all, the CrystalFontz 635 display is required.
o Secondly, two RAID1 arrays with three disks each is expected,
  /dev/sda, /dev/sdb, /dev/sdc.
- However, the input options allows you to switch off any of the two
  displays, e.g. you could use this client to display Nagios status only,
  in which case the RAID limitations above don't matter.
"""

"""Imports."""
import os, re, sys, socket, string, errno, signal, syslog, time, popen2
from datetime import datetime
from optparse import OptionParser

"""Globals."""
pgm = os.path.basename(sys.argv[0])
hostname = socket.gethostname()
opts = None
sock = None

def err(msg):
  """
  Print error message 'msg' on stderr if foreground process
  or to syslog if background process and then exit with 1.
  """
  if opts.foreground:
    if opts.verbose:
      now = datetime.now()
      print >> sys.stderr, \
	'%s %s %s[%d]: error: %s' % (now.strftime("%Y-%m-%d %H:%M:%S"), \
	hostname, pgm, os.getpid(), msg)
    else:
      print >> sys.stderr, '%s: %s' % (pgm, msg)
  else:
    syslog.openlog("lcdnmd",
      syslog.LOG_PID | syslog.LOG_CONS, syslog.LOG_DAEMON | syslog.LOG_USER)
    syslog.syslog(syslog.LOG_ERR, msg)
    syslog.closelog()
  if sock: sock.close()
  if filexists("/var/run/lcdnmd.pid"): os.unlink("/var/run/lcdnmd.pid")
  sys.exit(1)

def dbg(msg):
  "Print debug message 'msg' on stderr."
  if opts.debug: print >> sys.stderr, msg

class Bunch(dict):
  "Simplistic way of creating dict like objects that allows for dot notation."
  def __init__(self,**kw):
    dict.__init__(self,kw)
    self.__dict__.update(kw)

def filexists(filename):
  "Return True if a file exists, False otherwise."
  try: os.stat(filename)
  except OSError, e: return False
  return True

def signal_handler(sig, frame):
  "Simple signal handler."
  if sig == signal.SIGTERM:
    err('caught signal TERM (%d), terminating...' % (sig))
  else:
    err('caught unknown signal %d, aborting...' % (sig))

def detach():
  "Detach from terminal (run in background)."
  try:						# do the double fork magic...
    pid = os.fork()
    if pid > 0:					# exit first parent
      sys.exit(0)
  except OSError, e:
    err("fork#1 failed: %s" % (e.strerror))
    sys.exit(1)
						# decouple from parent environ
  os.chdir("/")					# don't prevent unmounting....
  os.setsid()
  os.umask(0)
  try:						# do second fork
    pid = os.fork()
    if pid > 0:					# exit from second parent
      open('/var/run/lcdnmd.pid', 'w').write('%d' % pid)
      sys.exit(0)
  except OSError, e:
    err("fork#2 failed: %s" % (e.strerror))
    sys.exit(1)

def send(s):
  "Simple wrapper for socket.send() including error handling."
  global sock
  try:
    dbg(s)
    sock.send("%s\n" % s)
  except socket.error, (errno, errmsg):
    err("%s[%d]: %s" % (opts.host, opts.port, errmsg))

def init_display():
  "Initialize the two display widgets."
  send("hello")				# always required...

  send("client_set %s" % (pgm))		# mdstat (RAID1) display...
  send("screen_add mds")
  send("screen_set mds")
  send("widget_add mds title title")
  send("widget_set mds title {RAID Monitor    %s}" % hostname)
  send("widget_add mds 2nd string")
  send("widget_add mds 3rd string")
  send("widget_add mds 4th string")

  send("client_set %s" % (pgm))		# Nagios display...
  send("screen_add nag")
  send("screen_set nag")
  send("widget_add nag title title")
  send("widget_set nag title {System Monitor    %s}" % hostname)
  send("widget_add nag 2nd string")
  send("widget_add nag 3rd string")
  send("widget_add nag 4th string")

def display(status, LEDs):
  "Get the collected info on to the actual display, and light up the LEDs."
  # Let's start with the RAID display widget...
  if opts.raid:
    for array in status.raid:
      if   array == "md0": r = 2; row = "2nd"
      elif array == "md1": r = 3; row = "3rd"
      else:
	err("again, no clue");
      A = status.raid[array].diskA
      B = status.raid[array].diskB
      C = status.raid[array].diskC
      if       A and     B and     C: st = "UUU"
      elif     A and     B and not C: st = "UU_"
      elif     A and not B and     C: st = "U_U"
      elif     A and not B and not C: st = "U__"
      elif not A and     B and     C: st = "_UU"
      elif not A and     B and not C: st = "_U_"
      elif not A and not B and     C: st = "__U"
      else:
	err("sorry, don't know what to do")
      if status.raid[array].finished:
	s = status.raid[array].finished
      else:
	s = ""
      send("widget_set mds %s 1 %d {%s: %d/%d [%s] %s}" % \
	(row,r,array,status.raid[array].active,status.raid[array].total,st, s))
      if status.raid[array].time_left:
	time_left = status.raid[array].time_left
      else:
	time_left = ""
      send("widget_set mds 4th 1 4 {%s}" % time_left)
  # ...and now on to the Nagios display widget...
  if opts.nagios:
    # First the hosts...
    s1 = "%2d OK" % status.nagios.hosts.Up
    s2 = ", %d Down"
    s3 = ", %d Unreach"
    if not status.nagios.hosts.Down: s2 = ""
    if not status.nagios.hosts.Unreach: s3 = ""
    send("widget_set nag 2nd 1 2 {H %s%s%s}" % (s1, s2, s3))
    # ...then the services...
    OK = status.nagios.services.OK
    C = status.nagios.services.Critical
    W = status.nagios.services.Warning
    U = status.nagios.services.Unknown
    OKs = "%2d OK" % OK
    Cs = ""
    Ws = ""
    Us = ""
    if not C and not W and U:	# 001 - 1
      Cs = ""
      Ws = ""
      Us = ", %d Unknown" % U
    elif not C and W and not U:	# 010 - 2
      Cs = ""
      Ws = ", %d Warning" % W
      Us = ""
    elif not C and W and U:	# 011 - 3
      Cs = ""
      Ws = ", %d Warn" % W
      Us = ", %d Uknown" % U
    elif C and not W and not U:	# 100 - 4
      Cs = ", %d Critical" % C
      Ws = ""
      Us = ""
    elif C and not W and U:	# 101 - 5
      Cs = ", %d Crit" % C
      Ws = ""
      Us = ", %d Unknown" % U
    elif C and W and not U:	# 110 - 6
      Cs = ", %d Crit" % C
      Ws = ", %d Warning" % W
      Us = ""
    elif C and W and U:		# 111 - 7
      Cs = ", %d C" % C
      Ws = ", %d W" % W
      Us = ", %d U" % U
    send("widget_set nag 3rd 1 3 {S %s%s%s%s}" % (OKs, Cs, Ws, Us))
    send("widget_set nag 4th 1 4 {%s     %s}" % \
      (status.nagios.uptime, status.nagios.age))
    # ...and finally, the LEDs...
    send("output %d" % LEDs)

def get_nagios_status():
  "Retrieve current host and services status from the nagiostats command."
  # Run the nagiostats command...
  try:
    f = os.popen(opts.nagiostats)
  except OSError, e:
    err("%s: %s" % (e.filename, e.strerror))
  # Find the lines in the output from nagiostats that we're interested in...
  hst = re.compile("^Hosts Up")
  srv = re.compile("^Services Ok")
  upt = re.compile("^Program Running Time")
  age = re.compile("^Status File Age")
  # The statuses retrieved are merely counters for each host/service state...
  for line in f.readlines():
    if hst.match(line):
      hosts = Bunch(Up      = string.atoi(string.split(line)[2]),
		    Down    = string.atoi(string.split(line)[4]),
		    Unreach = string.atoi(string.split(line)[6]))
    if srv.match(line):
      servs = Bunch(OK       = string.atoi(string.split(line)[2]),
                   Warning  = string.atoi(string.split(line)[4]),
                   Unknown  = string.atoi(string.split(line)[6]),
                   Critical = string.atoi(string.split(line)[8]))
    if upt.match(line):
      # Resulting format is: Dd HH:MM, where D is number of days.
      uptime = "%s %2.2d:%2.2d" % \
              (string.split(line)[3],
               string._int(string.split(line)[4].strip("h")),
               string._int(string.split(line)[5].strip("m")))
    if age.match(line):
      # Resulting format is: [HH:MM].
      stat_age = "[%2.2d:%2.2d]" % \
                 (string._int(string.split(line)[5].strip("m")),
                  string._int(string.split(line)[6].strip("s")))
  r = os.WEXITSTATUS(f.close() or 0)
  if r != 0: err("nagiostats: error: is nagios running?")
  return Bunch(hosts = hosts, services = servs, uptime = uptime, age = stat_age)

def get_raid_arrays():
  "Retrieve list of active RAID arrays, e.g. [md0, md1, ...]."
  raid_arrays = []
  "Use a regular expression to match the lines we're intrested in."
  expect = re.compile("^ARRAY[ \t]+/dev/md[0-9]+[ \t]+level=raid1")
  try:
    f = open("/etc/mdadm.conf", "r")
  except OSError, e:
    err("%s: %s" % (e.filename, e.strerror))
  for line in f:
    if expect.match(line):
      raid_arrays.append(string.split(string.split(line)[1], "/")[2])
  f.close()
  if raid_arrays == []:
    err("no RAID arrays found")
  return raid_arrays

def get_array_status(array):
  "Determine and return status for the three disks in one array."
  # The mdadm -QD command will give us the details we need.
  try:
    outf, inf = popen2.popen2("mdadm -QD /dev/%s" % array)
  except OSError, e:
    err("%s: %s" % (e.filename, e.strerror))
  inf.close()

  # Find the lines in the output that we're interested in...
  active = total = None
  expect = re.compile("^[ \t]+[0-9]+[ \t]+[0-9]+[ \t]+[0-9]+[ \t]+[0-9]+[ \t]+")
  sta    = re.compile("^[ \t]+State")
  act    = re.compile("^[ \t]+Active Devices")
  tot    = re.compile("^Working Devices")
  for line in outf.readlines():
    if expect.match(line):
      num = string.atoi(string.split(string.strip(line))[3])
      stat = string.split(string.strip(line))[4]
      if num == 0:
        if stat == 'active': A = True
	else: A = False
      elif num == 1:
        if stat == 'active': B = True
	else: B = False
      elif num == 2:
        if stat == 'active': C = True
	else: C = False
      else:
        err("internal: no idea")
    if sta.match(line):
      state = string.split(line)[2]
    if act.match(line):
      active = string.atoi(string.split(line)[3])
    if tot.match(line):
      total = string.atoi(string.split(line)[3])

  # Now, if any of the disks is in none active mode, there might just be a
  # chance that the disk is in 'spare rebuilding' (or resync) mode, in which
  # case we'll try to determine how much is done, in percent, and how much time
  # is left of the resync operation.
  finished = time_left = None
  if state != 'clean' or not A or not B or not C:
    try:
      f = open("/proc/mdstat", "r")
    except OSError, e:
      err("%s: %s" % (e.filename, e.strerror))
    # Find the lines in the output that we're interested in...
    expect = re.compile("^[ \t]+.+recovery")
    for line in f:
      if expect.match(line):
	# That's the percentage left to synchronize.
	finished = string.split(string.strip(line))[3]
	# And that's the time left until finished.
	time_left = "%s in %s" % \
	  (string.split(string.split(string.strip(line))[5], "=")[0],
	   string.split(string.split(string.strip(line))[5], "=")[1])

  return A, B, C, active, total, finished, time_left

def get_raid_status(arrays):
  status = {}
  for array in arrays:
    A, B, C, active, total, finished, time_left = get_array_status(array)
    status[array] = Bunch(diskA = A, diskB = B, diskC = C,
                          active = active, total = total,
			  finished = finished, time_left = time_left)
  return status

def get_LEDs(status):
  """
  Turn on the LEDs according to overall status.
  See the lcdleds client for details on how to set the LED values.
  There's four LEDs available on the CrystalFontz 635 display. From top to
  bottom: first one is used for overall status, the three remaining ones are
  used for showing off the RAID status for each of three disks.
  """
  # set the three disk LEDs...
  LEDs = 0
  if opts.raid:
    for array in status.raid:
      A = status.raid[array].diskA
      B = status.raid[array].diskB
      C = status.raid[array].diskC
      if status.raid[array].finished:	# sync in progress, make it yellow...
	if A: LEDs |=   2			# 2nd LED
	else: LEDs |=  34
	if B: LEDs |=   4			# 3rd LED
	else: LEDs |=  68
	if C: LEDs |=   8			# 4th LED
	else: LEDs |= 136
      else:				# no sync in progress, make it red...
	if A: LEDs |=   2
	else: LEDs |=  32
	if B: LEDs |=   4
	else: LEDs |=  64
	if C: LEDs |=   8
	else: LEDs |= 128
  # now set the 1st LED to reflect the overall status...
  if opts.nagios:
    if status.nagios.hosts.Down or status.nagios.services.Critical:
      LEDs |= 16	# 1st LED red
    elif status.nagios.hosts.Unreach or \
	 status.nagios.services.Warning or \
	 status.nagios.services.Unknown:
      LEDs |= 17	# yellow 
    else:
      LEDs |= 1	# green
  return LEDs

def init():
  "Get input options."
  global opts

  "Setup program input options."
  parser = OptionParser(version = "%prog 1.0.0")
  parser.add_option("-v", "--verbose", action="store_true", dest = "verbose",
    help = "verbose mode [%default]")
  parser.add_option("-g", "--debug", action="store_true", dest = "debug",
    help = "debug mode [%default]")
  parser.add_option("-F", "--foreground", action="store_true",
    dest = "foreground", help = "run in foreground [%default]")
  parser.add_option("-r", "--disable-raid", action="store_false",
    dest = "raid", help = "disable RAID monitoring")
  parser.add_option("-n", "--disable-nagios", action="store_false",
    dest = "nagios", help = "disable nagios monitoring")
  parser.add_option("-H", "--host", dest = "host",
    help = "LCD daemon hostname or IP address [%default]")
  parser.add_option("-p", "--port", dest = "port",
    help = "LCD daemon port number [%default]")
  parser.add_option("-i", "--interval", dest = "interval",
    help = "refresh value in seconds [%default]")
  parser.add_option("-N", "--nagiostats", dest = "nagiostats",
    help = "full path to nagiostats binary [%default]")
  parser.set_defaults(help = False, verbose = False, debug = False,
    foreground = False, raid = True, nagios = True,
    host = "localhost", port = 13666, interval = 1,
    nagiostats = "/usr/sbin/nagiostats")
  (opts, args) = parser.parse_args()
  if not opts.raid and not opts.nagios:
    err("cannot disable both raid and nagios, something's gotta' give'")

def set_signals():
  """
  Setup signal handling. TERM is the proper termination signal, and therefore
  the only one we act on. Other signals will have their default behaviour.
  """
  signal.signal(signal.SIGTERM, signal_handler)
  if opts.foreground:
    signal.signal(signal.SIGINT, signal_handler)

def main():
  "Detach + process forever."
  global sock

  init()					# Get the input options.
  filexists("/etc/mdadm.conf")			# Some trivial validations.
  filexists("/proc/mdstat")
  filexists("/usr/sbin/nagiostats")
  set_signals()					# Setup signal handling.
  if not opts.foreground:			# Start in background mode,
    detach()					# if applicable.
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Connect to LCDd...
  try:
    sock.connect((opts.host, opts.port))
  except socket.error, (errno, msg):
    err("%s[%d]: %s" % (opts.host, opts.port, msg))
  init_display()				# Initialize display widgets.
  while True:					# For ever...
    status = Bunch(raid = None, nagios = None)	# Instantiate.
    if opts.raid:				# Retrieve relevant status data.
      status.raid = get_raid_status(get_raid_arrays())
    if opts.nagios:
      status.nagios = get_nagios_status()
    display(status, get_LEDs(status))		# Do the actual display.
    time.sleep(opts.interval)			# Take it easy.

if __name__ == '__main__':
  main()
  sys.exit(0)
