#!/bin/bash
# apply_casacore_measures_tables.sh
#
# Install downloaded casacore measures tables atomically and verify it is in use.
#
# $Id$

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/casacore_measures_common.sh"


module add casacore  # add casacore bin dir to PATH to run the findmeastable program

update_id=$(get_latest)

# If not already in use, switch current symlink to the latest $dir_prefix/ *atomically* with an mv. Avoids race with a reader.
if [ "`readlink current`" != "$update_id" ]; then
  log INFO "Applying $update_id"
  ln -s "$update_id" "$working_dir/current_${update_id}" && mv -Tf "$working_dir/current_${update_id}" "$working_dir/current"
else
  log INFO "No new table to apply."
fi

# Check if casacore uses the just set up tables by extracting the path (token(s) 6,...) from findmeastable.
# If ok, findmeastable prints: "Measures table Observatories found as /home/jenkins/root/share/casacore/data/geodetic/Observatories"
if ! findmeastable > /dev/null; then exit 1; fi
used_dir=`findmeastable | cut -d' ' -f 6-`
if [ $? -ne 0 ]; then exit 1; fi
used_path=`readlink -f "$used_dir/../../.."`
if [ $? -ne 0 ]; then exit 1; fi
update_id_path="$working_dir/$update_id"
if [ "$update_id_path" != "$used_path" ]; then
  # potential improvement: revert if applied (and if it used to work) (e.g. empty $update_id/)
  fatal "It appears that the most recently set up measures tables are not in use. Most recent on the system is: '$update_id'."
fi

remove_old

log INFO "Done. The most recently retrieved measures data is (now) in use."
