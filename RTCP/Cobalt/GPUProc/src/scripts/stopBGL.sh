#!/bin/bash
# stopBGL.sh jobName observationID
#
# jobName       The name of the job
# observationID Observation number
#
# This script is called by OnlineControl when either:
#   - the stop time (plus a grace period) has passed
#   - the observation is aborted
#
# $Id$

if test "$LOFARROOT" == ""; then
  echo "LOFARROOT is not set! Exiting." >&2
  exit 1
fi

JOB="$1"
OBSID="$2"

# The name of what will be our parset
PARSET=$LOFARROOT/var/run/rtcp-$OBSID.parset

# The file to store the PID in
PIDFILE=$LOFARROOT/var/run/rtcp-$OBSID.pid

# The FIFO used for communication with rtcp
COMMAND_PIPE=$LOFARROOT/var/run/rtcp-$OBSID.pipe

source cobalt_functions.sh

function writecommand {
  PID=$1
  PIPE=$2
  CMD=$3

  # Send the stop command for a graceful shutdown
  COMMAND_HOST=`getCobaltHosts -C $PARSET`
  timeout 60s ssh $COMMAND_HOST "timeout 60s bash -c 'echo $CMD > $PIPE'"
}

(
# Always print a header, to match errors to observations
echo "---------------"
echo "called as: $0 $@"
echo "pwd:       $PWD"
echo "LOFARROOT: $LOFARROOT"
echo "obs id:    $OBSID"
echo "parset:    $PARSET"
echo "---------------"

function error {
  echo "$@" >&2
  exit 1
}

echo "PID file: $PIDFILE"

# Extract PID
PID=`cat $PIDFILE`
[ -n "$PID" ] || error "PID file empty: $PIDFILE"
echo "PID: $PID"

# Check whether the PID is valid
echo "Process:"
ps --no-headers -p "$PID" || error "Process not running: PID $PID"

# Send the stop command for a graceful shutdown
writecommand $PID $COMMAND_PIPE "stop" || error "Could not send 'stop' command"

# Remove command pipe (because startBGL.sh was its creator)
rm -f "$COMMAND_PIPE" || true

# Kill the process
# echo "Sending SIGTERM"

# TODO: Disabled actual killing, since MAC calls stopBGL.sh way too soon!
# kill "$PID" || error "Could not kill process: PID $PID"

# Done
echo "Done"

) 2>&1 | addlogprefix | tee -a $LOFARROOT/var/log/stopBGL.log

# Return the status of our subshell, not of tee
exit ${PIPESTATUS[0]}
