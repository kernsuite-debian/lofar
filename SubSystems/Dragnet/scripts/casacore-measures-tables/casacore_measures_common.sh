# casacore_measures_common.sh
# Source this file, don't execute it!
#
# $Id$

working_dir=/opt/IERS
dir_prefix=IERS-
measures_ftp_path=ftp://ftp.astron.nl/outgoing/Measures
measures_data_filename=WSRT_Measures.ztar
#measures_md5sum_filename=$measures_data_filename.md5sum
hostname=$(hostname)

# Example log() usage: log INFO "foo bar"
#   writes to stderr something like: node42 2015-10-16 16:00:46,186 INFO - foo bar
log() {
  loglevel=$1  # one of: DEBUG INFO WARN ERROR FATAL
  message=$2
  ts=`date --utc '+%F %T,%3N'`  # e.g. 2015-10-16 16:00:46,186
  echo "$hostname $ts $loglevel - $message" >&2
}

fatal() {
  log FATAL "$1"
  exit 1
}

# echo the directory component name of the most recent measures table.
# 'Most recent' is from name, not from last modified date!
get_latest() {
  if ! cd "$working_dir"; then fatal "Failed to cd to $working_dir"; fi
  local update_id
  update_id=`ls -d "$dir_prefix"* 2> /dev/null | tail -n 1`
  if [ -z "$update_id" ]; then
    # fatal since this function is to be called after an update has been retrieved and
    # unpacked (but not yet activated via the symlink).
    log FATAL "No existing casacore measures install recognized.";
  fi
  cd "$OLDPWD"  # 'cd -' echos the path altering func output :|
  echo "$update_id"
}

# Remove earlier downloaded entries beyond the 4 latest. ('ls' also sorts.)
remove_old() {
  if ! cd "$working_dir"; then fatal "Failed to cd to $working_dir"; fi
  old_update_ids=`ls -d "$dir_prefix"* 2> /dev/null | head -n -4`
  if [ ! -z "$old_update_ids" ]; then
    rm -rf $old_update_ids
    if [ $? -ne 0 ]; then
      log WARN "Failed to remove old measure tables dir(s)."  # not fatal
    else
      log INFO "Removed old measure tables dir(s): $old_update_ids"  # var contains newlines...
    fi
  fi
  cd "$OLDPWD"  # 'cd -' echos the path altering func output :|
}
