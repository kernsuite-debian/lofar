#!/bin/sh
# 1.2 check the GPS reception
# 03-05-2017 M.J. Norden

core=$(grep RS.HBA_SPLIT /opt/lofar/etc/RemoteStation.conf | cut -d'=' -f2)
echo "check Rubidium logging"

if [ $core = "Yes" ]
then
 echo "Note: THIS IS A CORE STATION. NO RUBIDIUM CLOCK INSTALLED!"
else
  tail -f /var/log/ntpstats/rubidium_log
fi

