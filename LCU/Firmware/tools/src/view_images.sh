# !/bin/bash
# version 2.2, date 28-11-2016,  M.J.Norden
station=`hostname -s`
let rspboards=`sed -n  's/^\s*RS\.N_RSPBOARDS\s*=\s*\([0-9][0-9]*\).*$/\1/p' /opt/lofar/etc/RemoteStation.conf`
ethport=`grep RSPDriver.IF_NAME /opt/lofar/etc/RSPDriver.conf | awk -F= '{print $2}'`

echo "This station is "$station
echo "The number of rspboards is "$rspboards
echo "The ethernet port is "$ethport

for ((ind=0; ind < $rspboards; ind++)) do
  MACadr=$(printf "10:FA:00:00:%02x:00" $ind)
  sudo rsuctl3 -i $ethport -q -m $MACadr -V
  sudo rsuctl3 -i $ethport -q -m $MACadr -l
done
