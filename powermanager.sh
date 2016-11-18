#!/bin/bash

if [ ! -d /sys/class/gpio/gpio199/ ]; then
  echo 199 > /sys/class/gpio/export
  logger "Exporting gpio199"
fi
if [ ! -d /sys/class/gpio/gpio200/ ]; then
  echo 200 > /sys/class/gpio/export
  logger "Exporting gpio200"
fi

if grep -q out "/sys/class/gpio/gpio199/direction"; then
   echo in > /sys/class/gpio/gpio199/direction
   logger "Setting gpio99 as out"
fi

if grep -q out "/sys/class/gpio/gpio200/direction"; then
   echo in > /sys/class/gpio/gpio200/direction
   logger "Setting gpio200 as out"
fi

#echo in > /sys/class/gpio/gpio199/direction
#echo in > /sys/class/gpio/gpio200/direction

get_ac_status() {
    ac1=`cat /sys/class/gpio/gpio199/value`
    ac2=`cat /sys/class/gpio/gpio200/value`

    if [ "0$ac1" -eq 1 -o "0$ac2" -eq "1" ]; then
        export ACJACK="off"
    else
        export ACJACK="on"
    fi
}

get_lock_status() {
    if [ -e "/tmp/shutdown.lock" ]; then
        export LOCK="true"
    else
        export LOCK="false"
    fi
}

while :
do
    get_ac_status
    get_lock_status

    if [[ "$ACJACK" == "off" && "$LOCK" == "false" ]]; then
        logger "Shutting down soon"
        touch /tmp/shutdown.lock
        shutdown --no-wall -P 5
    elif [[ "$ACJACK" == "on" && "$LOCK" == "true" ]]; then
        logger "Power restored. Shutdown cancelled."
        shutdown --no-wall -c
        rm /tmp/shutdown.lock
    fi

    sleep 1;
done

