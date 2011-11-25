!#/bin/bash
## Copies stuff to the right places

LCDPROCSRC=/usr/src/lcdproc/
CARTRACKERSRC=/usr/src/cartracker/

cd $LCDPROCSRC
./configure --enable-drivers=SureElec --prefix=/usr
make install

cp $LCDPROCSRC/scripts/debian/lcdproc.init /etc/init.d/lcdproc
cp CARTRACKERSRC/LCD
chmod +x /etc/init.d/lcdproc
update-rc.d lcdproc defaults

cd $CARTRACKERSRC

