#!/bin/bash

# Spin in a 1 second loop, check for current speed and call to exit if stopped for over a minute

MONITORFILE=monitor.nmea
WORKINGDIR=$1
OUTPUTDIR=$1
PREVIOUSSTATE=0
GPSPIPEMONITORPIDFILE=/var/run/gpspipemonitor.pid

function checkoutputdir {
        # Check for output directory, and bail if not present
        if [ -e "$OUTPUTDIR" ]; then                             # test to see if $OUTPUTDIR exists
                echo Output directory $OUTPUTDIR does exist. Rejoice.
        else
                echo Output directory $OUTPUTDIR not present. Creating $OUTPUTDIR
        fi
}

checkoutputdir

touch $MONITORFILE # Due to gpspipe taking a while to start up
gpspipe -r > $OUTPUTDIR/$MONITORFILE &
EXIT=$?
if [ "$EXIT" = "0" ]; then                             # It's not running
	echo "gpspipe started"
        echo $! > $GPSPIPEMONITORPIDFILE                # Dump PID to file for later use
elif [ "$EXIT" = "1" ]; then                            # It is running... bail out
	echo "monitor gpspipe failed to start"
	# need proper exit code handling here and in caller
	exit
fi

while true
do

sleep 1

awk -F , '$1=="$GPGGA" {print}' $OUTPUTDIR/$MONITORFILE | tail -n 1 > $OUTPUTDIR/gps_GPGGA
awk -F , '$1=="$GPRMC" {print}' $OUTPUTDIR/$MONITORFILE | tail -n 1 > $OUTPUTDIR/gps_GPRMC
awk -F , '$1=="$GPGSA" {print}' $OUTPUTDIR/$MONITORFILE | tail -n 1 > $OUTPUTDIR/gps_GPGSA
awk -F , '$1=="$GPRMC" {print $3}' $OUTPUTDIR/gps_GPRMC | tail -n 1 > $OUTPUTDIR/gps_valid

good_pos=$(cat $OUTPUTDIR/gps_valid)
case $good_pos in
        V)      LOCK=0
		# V stands for VOID
		# echo GPS Data is NOT VALID !!!
                echo "?" > $OUTPUTDIR/gps_latitude
                echo "?" > $OUTPUTDIR/gps_longitude
                echo "?" > $OUTPUTDIR/gps_altitude
                awk -F , '$MONITORFILE=="$GPGGA" {print $8}' $OUTPUTDIR/gps_GPGGA > $OUTPUTDIR/gps_sats_in_view
                echo "?" > $OUTPUTDIR/gps_heading
                echo "?" > $OUTPUTDIR/gps_speed
		echo "?" > $OUTPUTDIR/gps_fixtime

                ;;                      
        A)      LOCK=1
		# A stands for Active
		# echo GPS Data is valid
                awk -F , '$1=="$GPGGA" {print $3 $4}' $OUTPUTDIR/gps_GPGGA > $OUTPUTDIR/gps_latitude
                awk -F , '$1=="$GPGGA" {print $5 $6}' $OUTPUTDIR/gps_GPGGA > $OUTPUTDIR/gps_longitude
                awk -F , '$1=="$GPGGA" {print $10 $11}' $OUTPUTDIR/gps_GPGGA > $OUTPUTDIR/gps_altitude
                awk -F , '$1=="$GPGGA" {print $8}' $OUTPUTDIR/gps_GPGGA > $OUTPUTDIR/gps_sats_in_view                   
                awk -F , '$1=="$GPRMC" {print $9}' $OUTPUTDIR/gps_GPRMC > $OUTPUTDIR/gps_heading
                awk -F , '$1=="$GPRMC" {print $8}' $OUTPUTDIR/gps_GPRMC > $OUTPUTDIR/gps_speed
                awk -F , '$1=="$GPGGA" {print $7}' $OUTPUTDIR/gps_GPGGA > $OUTPUTDIR/gps_quality
                awk -F , '$1=="$GPGGA" {print $2}' $OUTPUTDIR/gps_GPGGA > $OUTPUTDIR/gps_fixtime
                awk -F , '$1=="$GPGSA" {print $3}' $OUTPUTDIR/gps_GPGSA > $OUTPUTDIR/gps_fixtype

                ;;
        esac
	#This is where we should be converting things into usable values
	#Like gps_fixtype into No fix, 2D and 3D (1, 2, 3 respectively)
	clear
        echo    
	echo previous____: $PREVIOUSSTATE
	echo lock________: $LOCK
        echo lat_________: $(cat $OUTPUTDIR/gps_latitude)
        echo lon_________: $(cat $OUTPUTDIR/gps_longitude)
        echo altitude____: $(cat $OUTPUTDIR/gps_altitude)
        echo sats_in_view: $(cat $OUTPUTDIR/gps_sats_in_view)
        echo heading_____: $(cat $OUTPUTDIR/gps_heading)°     
	echo quality_____: $(cat $OUTPUTDIR/gps_quality)
	echo fixtime_____: $(cat $OUTPUTDIR/gps_fixtime)
	echo fixtype_____: $(cat $OUTPUTDIR/gps_fixtype)
        speed=$(cat $OUTPUTDIR/gps_speed)
        if [ "$speed" = "" ]; then
                speed=0
        fi      
        echo speed_______: $speed knots 

	#if [[ $PREVIOUSSTATE="0" && $LOCK="1" ]]; then
	if [ "$PREVIOUSSTATE" -eq 0 -a "$LOCK" -eq 1 ]; then

		## Start logging
		echo We got a lock!
		PREVIOUSSTATE=1
		echo /home/kyleg/scripts/gpxtracker.sh startlog

	fi

	#if [ $PREVIOUSSTATE=1 ] && [ $LOCK=0 ]; then
        if [ "$PREVIOUSSTATE" -eq 1 -a "$LOCK" -eq 0 ]; then
		
		## Stop logging
		echo "We lost the lock! :-("
		PREVIOUSSTATE=0
		echo /home/kyleg/scripts/gpxtracker.sh stoplog	
	fi

done

