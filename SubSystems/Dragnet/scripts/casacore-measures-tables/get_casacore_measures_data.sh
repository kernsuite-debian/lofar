#!/bin/bash
# get_casacore_measures_tables.sh
#
# Retrieve new casacore measures tables under $working_dir and extract. Written for jenkins@fs5 (DAS-4).
# If it works out, remove very old download dirs starting with $dir_prefix.
#
# $Id$

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/casacore_measures_common.sh"


# Get the data (~12 MB) from the server. This may take up to 10s of seconds for a slow FTP server.
# By default, when wget downloads a file, the timestamp is set to match the timestamp from the remote file.
download()
{
  wget -N --tries=4 \
    $measures_ftp_path/$measures_data_filename #\
    #$measures_ftp_path/$measures_md5sum_filename
}

# Verify that md5 hash is equal to hash in $measures_md5sum_filename  (no longer used, was used for measures tables from CSIRO)
# No need to compare the filename. (If from CSIRO, note that the .md5sum contains a CSIRO path.)
check_md5()
{
  local md5sum=`cut -f 1 -d ' ' $measures_md5sum_filename`
  if [ $? -ne 0 ]; then return 1; fi
  local data_md5=`md5sum $measures_data_filename | cut -f 1 -d ' '`
  if [ -z "$data_md5" ]; then return 1; fi

  if [ "$md5sum" != "$data_md5" ]; then
    log ERROR "Computed and downloaded MD5 sums do not match."
    return 1
  fi

  return 0
}

# Check that the measures tables under tmp_$update_id/data are up-to- date.
check_uptodate()
{
  # Only check last int, but set options all and verbose as example cmd to manually run on error.
  check_out=$("$working_dir"/CheckIERS dir="$update_id/data" all=true verbose=true) || return 1
  nrdays=$(echo "$check_out" | tail -1 | awk '{print $5}') || return 1
  [ $nrdays -ge 7 ]  # IERS prediction for at least 7 more days?
}


update_id=$dir_prefix`date --utc +%FT%T.%N`  # e.g. IERS-2015-09-26T01:58:30.098006623
if [ $? -ne 0 ]; then exit 1; fi

# Use a tmp_ name until written and checked, then move into place.
if ! cd "$working_dir" || ! mkdir -p "tmp_$update_id/data" || ! cd "tmp_$update_id/data"; then
  fatal "Failed to create and cd to tmp_$update_id/data"
fi
if ! download; then  # || ! check_md5; then
  rm -f $measures_data_filename
  log ERROR "Download failed. Retrying once."
  sleep 2
  if ! download; then  # || ! check_md5; then
    rm -f $measures_data_filename #$measures_md5sum_filename
    cd ../.. && rm -rf "tmp_$update_id"
    fatal "Download failed again."
    exit 1
  fi
fi

if ! tar zxf $measures_data_filename; then
  cd ../.. && rm -rf "tmp_$update_id"
  exit 1
fi

cd ../.. || exit 1  # back to $working_dir

# Make it available to the apply script to install/move it at an opportune moment.
if ! mv "tmp_$update_id" "$update_id"; then
  # On error, leave the tmp_ dir in place for manual inspection.
  fatal "Failed to prepare measures tables update 'tmp_$update_id'. Manual intervention required."
fi

if ! check_uptodate; then fatal "Verification of downloaded measures tables failed."; fi

log INFO "Done. Measures tables update '$update_id' ready to be applied."
