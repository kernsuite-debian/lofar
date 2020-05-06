#!/bin/bash
# cron-update-IERS-DRAGNET.sh
#
# Updates casacore measures tables on the DRAGNET cluster under /opt/IERS/
# To be started once per week (or so) via cron as 'lofarsys:dragnet' on any single node.
# lofarsys' crontab (every Mon, 04:00 AM):
#   0 4 * * 1 /opt/IERS/cron-update-IERS-DRAGNET.sh 2> /home/lofarsys/lofar/var/log/IERS/cron-update-IERS-DRAGNET.log
#
# Caveats: If any cluster node is unreachable, the update is not applied.
#   This is intentional, but when at least one node is down often, this is unworkable.
#   The solution is *not* a partial install, but to create a proper software package
#   that every node pulls on a fixed time in the week and upon boot before starting slurmd.
#
# $Id$

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/casacore_measures_common.sh"


nodelist="dragnet dragproc $(seq -s ' ' -f drg%02g 1 23)"
log INFO "Started. Node list: $nodelist"

log INFO "Retrieving fresh copy of casacore measures archive file"
"$working_dir/get_casacore_measures_data.sh" || exit 1

latest=$(get_latest)
path="$working_dir/$latest/data/$measures_data_filename"
log INFO "Transferring archive '$path' across the cluster"
declare -a status_arr1
declare arr1_i=0
for host in $nodelist; do
  scp -p -q -o BatchMode=yes -o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no "$path" "$host:$working_dir" &
  status_arr1[$arr1_i]=$!
  ((arr1_i++)) || true
done
for ((i = 0; i < $arr1_i; i++)); do
  log DEBUG "Waiting for pid ${status_arr1[$i]}"
  wait ${status_arr1[$i]} || exit 1
done

log INFO "Putting archive content in place on other nodes"
declare -a status_arr2
declare arr2_i=0
for host in $nodelist; do
  # Escape double quotes below the following line!
  ssh -q -o BatchMode=yes -o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no $host "
    hostname &&
    cd /opt/IERS &&
    mkdir -p \"$latest/data\" &&
    mv \"$measures_data_filename\" \"$latest/data\" &&
    cd \"$latest/data\" &&
    tar zxf \"$measures_data_filename\" &&
    cd ../.. &&
    chgrp -R dragnet \"$latest\"
  " >&2 &
  status_arr2[$arr2_i]=$!
  ((arr2_i++)) || true
done
for ((i = 0; i < $arr2_i; i++)); do
  log DEBUG "Waiting for pid ${status_arr2[$i]}"
  wait ${status_arr2[$i]} || exit 1
done

log INFO "Applying update across the cluster"
declare -a status_arr3
declare arr3_i=0
for host in $nodelist; do
  # Escape double quotes below the following line!
  ssh -q -o BatchMode=yes -o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no $host "
    hostname &&
    \"$working_dir/apply_casacore_measures_data.sh\"
  " >&2 &
  status_arr3[$arr3_i]=$!
  ((arr3_i++)) || true
done
for ((i = 0; i < $arr3_i; i++)); do
  log DEBUG "Waiting for pid ${status_arr3[$i]}"
  wait ${status_arr3[$i]} || exit 1
done

log INFO "Done"
