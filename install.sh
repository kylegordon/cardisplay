#!/bin/bash
## Copies stuff to the right places

LCDPROCSRC=/usr/src/lcdproc/
CARTRACKERSRC=/usr/src/cartracker/
LCDPROCETC=/etc/lcdproc/

mkdir $LCDPROCETC

cd $LCDPROCSRC
./configure --enable-drivers=SureElec --prefix=/usr
make install

cp $LCDPROCSRC/scripts/debian/lcdproc.init /etc/init.d/lcdproc
cp $LCDPROCSRC/scripts/debian/lcdproc.LCDd.init /etc/init.d/LCDd
cp $CARTRACKERSRC/LCDd.conf $LCDPROCETC/
cp $LCDPROCSRC/scripts/debian/lcdproc.LCDd.default /etc/default/LCDd
chmod +x /etc/init.d/lcdproc
chmod +x /etc/init.d/LCDd
update-rc.d lcdproc defaults
update-rc.d LCDd defaults

## Enable LCDd
sed -i -e s/START=no/START=yes/ /etc/default/LCDd
sed -i -e s/#CONFIGFILE/CONFIGFILE/ /etc/default/LCDd

cd $CARTRACKERSRC

