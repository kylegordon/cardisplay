#!/bin/bash
#20:38 < mgdm> bagpuss_thecat: there is an NMEA sentence called GPRMC, which has the speed in knots and track angle for you - my GPS at least outputs it
#20:38 < mgdm> reference at http://www.gpsinformation.org/dale/nmea.htm#RMC

DATE=`date +%m%d%H%M`
OUTPUTDIR=/var/lib/gpxtracker/
OUTPUTFILE=$OUTPUTDIR/$DATE 					# OUTPUTFILE doesn't have a suffix as it's used for pre and post processing filenames (nmea and gpx)
SAVEDIR=/var/log/gpxtracker/
LOCKFILE=/var/lock/gpspipe.lck
GPSPIPELOGGERPIDFILE=/var/run/gpspipelogger.pid
GPXMONITORPIDFILE=/var/run/gpxtrackermonitor.pid
GPSPIPEMONITORPIDFILE=/var/run/gpspipemonitor.pid
INFOFILE=/var/run/gpxtracker.inf
MYAPMAC=
MYGPSMAC=00:0A:3A:02:E9:E0

################ Note to self ####################
### Start gpspipe, use it to gather data on satellite coverage
### When gpxtrackermonitor reveals a lock, call gpxtracker to start logging
### Start gpspipe, and use the output to monitor signal. When lock achieved, do something to start saving the output (may involve restarting gpspipe and tee

##################################################

function start_monitor {

        # Start the gpxtrackermonitor.sh script
 	#/home/kyleg/scripts/gpxtrackermonitor.sh $OUTPUTFILE.nmea $OUTPUTDIR &
	`pwd`/gpxtrackermonitor.sh $OUTPUTDIR &
        EXIT=$?
        if [ "$EXIT" = "0" ]; then                             # It's not running
                echo "gpstrackermonitor started"
                echo $! > $GPXMONITORPIDFILE                   # Dump PID to file for later use
        elif [ "$EXIT" = "1" ]; then                           # It is running... bail out
                echo "gpxtrackermonitor failed to start"
                exit
        fi

}


function start_logging {

	#Rebind rfcomm0 for safety sake, cos it's a bit naff...
	#rfcomm release rfcomm0
	#rfcomm bind rfcomm0

	#Restart GPSD, cos it doesn't seem to handle disconnects very well
	#/etc/init.d/gpsd restart

	## All of the above is now commented out as the GPS reciever is a wired one. No bluetooth disconnect nastiness

	#Begin logging and background it
	echo "Starting logging to $OUTPUTFILE.nmea"
	gpspipe -r > $OUTPUTFILE.nmea &
	EXIT=$?
        if [ "$EXIT" = "0" ]; then                             # It's not running
                echo "logger gpspipe started"
	        echo $! > $GPSPIPELOGGERPIDFILE			# Dump PID to file for later use
		echo $OUTPUTFILE > $INFOFILE			# Store the name of the file that we're saving to for later use in stop & convert
        elif [ "$EXIT" = "1" ]; then                            # It is running... bail out
                echo "logger gpspipe failed to start"
		rm $LOCKFILE
		exit
        fi

}

function stop_logging {
	# TODO Check to see if listed AP is nearby. Upload with 5 minute timeout if it is. Shutdown immediately if it isn't.
	ps waux | grep -i [g]pspipe > /dev/null		# Check to see if gpspipe is running	
	EXIT=$?
	if [ "$EXIT" != "0" ]; then				# It's not running
	        echo "gpspipe is not running!"
	elif [ "$EXIT" = "0" ]; then				# It is running... kill, translate and unlock
	        GPXLOGGERPID=`cat $GPSPIPELOGGERPIDFILE`
		OUTPUTFILE=`cat $INFOFILE`
	        echo Stopping logger gpspipe, pid $GPXLOGGERPID
        	kill $GPXLOGGERPID
        	rm $GPSPIPELOGGERPIDFILE
		rm $LOCKFILE
		echo -n "Translating NMEA to GPX... "
		gpsbabel -i nmea -f $OUTPUTFILE.nmea -o gpx -F $OUTPUTFILE.gpx
		echo "done"
		EXIT=$?
		if [ "$EXIT" = "0" ]; then
			echo rm $OUTPUTFILE.nmea
		else
			echo "Failed to convert. Now exiting"
		fi
        fi

}

function stop_monitor {
	# stop the gpx monitor
        ps waux | grep -i [g]pxtrackermonitor > /dev/null         # Check to see if gpxtrackermonitor is running
        EXIT=$?
        if [ "$EXIT" != "0" ]; then                             # It's not running
                echo "gpxtrackermonitor is not running!"
        elif [ "$EXIT" = "0" ]; then                            # It is running... kill it!
                echo Stopping gpxtrackermonitor, pid `cat $GPXMONITORPIDFILE`
                kill `cat $GPXMONITORPIDFILE`
        fi


	#stop the monitor gpspipe instance
        ps waux | grep -i [g]pspipe > /dev/null         # Check to see if gpspipe is running
        EXIT=$?
	if [ "$EXIT" != "0" ]; then                             # It's not running
                echo "gpspipe is not running!"
        elif [ "$EXIT" = "0" ]; then                            # It is running... kill, translate and unlock
                GPSPIPEMONITORPID=`cat $GPSPIPEMONITORPIDFILE`
                echo Stopping monitor gpspipe, pid $GPSPIPEMONITORPID
                kill $GPSPIPEMONITORPID
                rm $GPSPIPEMONITORPIDFILE
        fi



}

function check_ap {
	#Check wireless access point and upload
	echo Checking AP

	# echo Found AP with MAC XX:XX:XX:XX:XX:XX
    	ping -c 5 64.233.169.103 > /dev/null
    	if [ "$?" -eq 0 ]; then
        	kdialog --msgbox "Internet Lost";
    	else
        	sleep 30
        main
    	fi
}

function upload_data {

	# Check that $OUTPUTDIR is not empty and upload any gpx files that exist.
	find . /var/lib/gpxtracker/ -iname *.gpx -exec ls -l {} \;

	# We check for known access points before uploading data.
	check_ap

	#Send the data to OSM
	echo "Uploading data"

}

function checklock {
        # Check for lockfile, and bail if present
        if [ -e "$LOCKFILE" ]; then                             # test to see if $LOCKFILE exists
                echo "Lockfile present, exiting"
                ps waux | grep -i [g]ps > /dev/null		# test to see if gpspipe is also running
        	EXIT=$?
        	if [ "$EXIT" = "0" ]; then
                	echo "gpspipe is already running"
		fi
		exit 0
        else
                touch $LOCKFILE
        fi
}


if [ "$1" = "check_ap" ]; then

        check_ap

elif [ "$1" = "start" ]; then

	#Check for lockfile
        checklock
	start_monitor
        start_logging

elif [ "$1" = "upload" ]; then

	upload_data

elif [ "$1" = "stoplog" ]; then

        stop_logging

elif [ "$1" = "stop" ]; then

        stop_logging
	stop_monitor

elif [ "$1" = "startlog" ]; then

        start_logging

else

        echo No options provided, try passing the start parameter
        exit 64                                         ## Exit with command line usage error
fi

