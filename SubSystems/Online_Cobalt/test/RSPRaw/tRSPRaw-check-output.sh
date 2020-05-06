#!/bin/bash
#
# tRSPRaw output is quite big, so instead of diff-ing to a reference output,
# check some properties in this script.
#
# $Id$

if [ $# -ne 2 ]; then
  echo 'Syntax: tRSPRaw-check-output.sh <test-input-dir> <test-output-dir>' >&2
  exit 1
fi

INDIR="$1"
OUTDIR="$2"

# from the .parset:
IN_FILENAME1="$INDIR/tRSPRaw_tmp.raw1.udp"
IN_FILENAME2="$INDIR/tRSPRaw_tmp.raw2.udp"
OUT_FILENAME1="$OUTDIR/L102030_CS002HBA0_0_rsp.raw"
OUT_FILENAME2="$OUTDIR/L102030_CS501HBA0_0_rsp.raw"
TIMESTAMP_PATTERN="14:15:"  # to exclude the first N packets in IN_FILENAME* with timestamps before RSP raw start time

# Check input vs output on number of RSP packets and their sample number written between parset RSPRaw start/stop time.
# Echo files to compared, since the diff cmd below compares /dev/fd/N filedescriptors, which gives a useless error message.
echo 'tRSPRaw-check-output.sh: doing rough check using diff(1) and printRSP (source under InputProc/src/Station/) on generated RSP raw input and output files'
echo "tRSPRaw-check-output.sh: diff 1: $IN_FILENAME1 (filtered) vs $OUT_FILENAME1"
echo "tRSPRaw-check-output.sh: diff 2: $IN_FILENAME2 (filtered) vs $OUT_FILENAME2"
printRSP < /dev/null || exit $?  # exit 127 if printRSP not found (the next cmds do not)
diff -q <(printRSP < "$IN_FILENAME1"  | grep "Time stamp:   Thu Dec  5 $TIMESTAMP_PATTERN") \
        <(printRSP < "$OUT_FILENAME1" | grep "Time stamp:   Thu Dec  5 $TIMESTAMP_PATTERN") \
&& \
diff -q <(printRSP < "$IN_FILENAME2"  | grep "Time stamp:   Thu Dec  5 $TIMESTAMP_PATTERN") \
        <(printRSP < "$OUT_FILENAME2" | grep "Time stamp:   Thu Dec  5 $TIMESTAMP_PATTERN")

