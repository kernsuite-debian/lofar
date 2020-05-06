#!/bin/bash
echo "Begin `date`"
echo "Host  `hostname`"

set -u
#set -x

RSPCONNECTIONS=${LOFARROOT:-/opt/lofar}/etc/StaticMetaData/RSPConnections_Cobalt.dat

# Get a list of my MAC addresses
MYMACS=`cat /sys/class/net/*/address | sort | uniq`

ILT_STATIONS_SENDING_TO_ME=`
  for MAC in $MYMACS; do
    # Select all stations going to one of my MAC addresses
    fgrep -i $MAC $RSPCONNECTIONS |
    # Avoid comments
    grep -v "^#" |
    # Select ILT stations only (name is xx6xx).
    grep "^..6.. "
  done
`

echo The following stations send to us:
echo "$ILT_STATIONS_SENDING_TO_ME"
echo ""

# Construct IPs to ping, one or more per station
RSPBOARD_IPS=`
echo "$ILT_STATIONS_SENDING_TO_ME" |
  perl -ne '
    if (/^..60?(..?) .* 10[.]([0-9]+)[.]([0-9]+)[.]2../) {
      # Parse our IP, and construct IP of first RSP board
      if ($3 == 1) {
        print "10.$2.$1.1\n"
      } else {
        print "10.$2.$3.1\n"
      }
    } '
`

echo IPs of RSP boards to ping: $RSPBOARD_IPS

for IP in $RSPBOARD_IPS
do
  # Ping this RSP board, but don't wait for an answer
  ping -p 10fa -q -n -c 2 -i 0.5 -w 1 $IP
done

echo "End   `date`"
