#!/bin/bash
#
# CobaltControl.sh is the interface for `swlevel' to see
# which observations are running, and to kill them if requested.
#
# $Id$

COMMAND=$1

function procname() {
  # the basename of this script, without its extension
  basename -- "$0" | sed 's/[.][^.]*$//g'
}

shopt -s nullglob

case $COMMAND in
  start)
    # no-op
    ;;

  stop)
    for PIDFILE in $LOFARROOT/var/run/rtcp-*.pid
    do
      PID=`cat $PIDFILE`
      echo "Softly killing rtcp(${PID})"
      kill -15 $PID
    done
    ;;

  status)
    SWLEVEL=$2

    PIDS=""
    OBSIDS=""
    for PIDFILE in $LOFARROOT/var/run/rtcp-*.pid
    do
      # only include PID if process is still running
      PID=`cat $PIDFILE`
      PID=`ps -o pid --no-heading -p $PID`

      if [ -n "$PID" ]; then
        PIDS="$PIDS $PID"
        OBSIDS="$OBSIDS `echo $PIDFILE | perl -ne '/rtcp-([0-9]+).pid/; print $1;'`"
      fi
    done

    if [ -z "$OBSIDS" ]
    then
      printf "%d : %-25s DOWN\n" "$SWLEVEL" "`procname`"
    else
      printf "%d : %-25s %s %s\n"   "$SWLEVEL" "`procname`" "$PIDS" "[ObsID:$OBSIDS]"
    fi
    ;;

  *)
    echo "usage: $0 {start|stop|status}"
    ;;
esac
