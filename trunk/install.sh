#!/bin/bash
## Copies stuff to the right places

LCDPROCSRC=/usr/src/lcdproc/
CARTRACKERSRC=/usr/local/cartracker/trunk/
LCDPROCETC=/etc/lcdproc/
CARTRACKERETC=/etc/cartracker/

mkdir $LCDPROCETC
mkdir $CARTRACKERETC

cd $LCDPROCSRC
./configure --enable-drivers=SureElec --prefix=/usr
make install

cp $LCDPROCSRC/scripts/debian/lcdproc.LCDd.init /etc/init.d/LCDd
cp $CARTRACKERSRC/LCDd.conf $LCDPROCETC/
cp $LCDPROCSRC/scripts/debian/lcdproc.LCDd.default /etc/default/LCDd
chmod +x /etc/init.d/LCDd
update-rc.d LCDd defaults

## Enable LCDd
sed -i -e s/START=no/START=yes/ /etc/default/LCDd
sed -i -e s/#CONFIGFILE/CONFIGFILE/ /etc/default/LCDd
## Do something to update DriverPath in LCDd.conf

cd $CARTRACKERSRC
cp cartracker-init /etc/init.d/cartracker
cp cartracker-default /etc/default/
cp cartracker.cfg.example $CARTRACKERETC
update-rc.d cartracker defaults
