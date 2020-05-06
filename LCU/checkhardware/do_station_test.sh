#!/bin/bash


 # default values
START=""
STOP=""
LEVEL=0
UPDATE="no"
SERVICE="yes"
HELP="no"

# get command line options
while getopts s:e:tTurh option
do
    case "${option}"
    in
        s) START=${OPTARG};;
        e) STOP=${OPTARG};;
        t) LEVEL=1;;
        T) LEVEL=2;;
        u) UPDATE="yes";;
        r) SERVICE="yes";;
        h) HELP="yes";;
    esac
done

if [ $HELP == "yes" ]
then
    echo "Usage:"
    echo "   do_station_test.sh -s 20130624_04:00:00 -e 20130624_06:00:00 -u"
    echo "   -s : start time"
    echo "   -e : end time"
    echo "   -u : update pvss"
    echo "   -t : do short test L1"
    echo "   -T : do long test L2"
    echo "   -r : do service test and show results (default)"
    echo "   -h : show this screen"
    exit
fi

hostname=`hostname -s`
host=`echo "$hostname" | awk '{ print toupper($1) }'`

cd /opt/stationtest/

# set filenames and dirs
local_data_dir="/opt/stationtest/data/"
global_data_dir="/globalhome/log/stationtest/"

if [ $LEVEL -ne 0 ]
then
    SERVICE="no"
fi

filenameNow=$host"_station_test.csv"
if [ $SERVICE == "yes" ]
then
    LEVEL=2
    filenameLocal=$host"_S_StationTest.csv"
    filenameLocalHistory=$host"_S_StationTestHistory.csv"
else
    filenameLocal=$host"_L"$LEVEL"_StationTest.csv"
    filenameLocalHistory=$host"_L"$LEVEL"_StationTestHistory.csv"
fi
filenameBadRCUs=$host"_bad_rcus.txt"

# set test level
level="-l="$LEVEL

# set start and stop time if given
start=""
stop=""
if [ -n "$STOP" ]
then
    echo "STOP not empty"
    if [ -n "$START" ]
    then
        echo "START not empty"
        start="-start="$START
    fi
    stop="-stop="$STOP
fi

echo "Running check_hardware.py $level $start $stop"
# Check hardware
if [ $SERVICE == "yes" ]
then
    ./check_hardware.py $level $start $stop -ls=info
else
    ./check_hardware.py $level $start $stop
fi

err=$?
echo "Exit code from check_hardware.py is " $err
# Accepts exit code 0 that means successfully executed,
# and exit code 120 that means the the python3 interpreter cannot
# flush the stdout buffer. This is a feature of the python3 interpreter,
# that manifests itself with a headless execution of the current script.

if [ $err -eq 0 ] || [ $err -eq 120 ]
then
    # Add test results too PVSS and make bad_rcu_file
    #updatePVSS.py -N=5,50,1 -J=5,50,2 -S=20 -E
    #new settings by Wilfred, 9-7-2013
    if [ $UPDATE == "yes" ]
    then
        ./update_pvss.py -N=5,50,3 -J=5,50,3 -E -S=10 -LBLN=5,50,3 -LBLJ=5,50,3 -LBLS=10 -LBHN=5,50,3 -LBHJ=5,50,3 -LBHS=10
    else
        ./update_pvss.py -no_update -N=5,50,3 -J=5,50,3 -E -S=10 -LBLN=5,50,3 -LBLJ=5,50,3 -LBLS=10 -LBHN=5,50,3 -LBHJ=5,50,3 -LBHS=10
    fi

    # Copy to local filename  file in local dir
    echo "copying file $local_data_dir$filenameNow into $local_data_dir$filenameLocal"
    cp $local_data_dir$filenameNow $local_data_dir$filenameLocal
    echo "copied file $local_data_dir$filenameNow into $local_data_dir$filenameLocal"

    # Add to history
    echo "concatenating to station tests history" $local_data_dir$filenameNow $local_data_dir$filenameLocalHistory
    cat $local_data_dir$filenameNow >> $local_data_dir$filenameLocalHistory
    echo "concatenated to station tests history" $local_data_dir$filenameNow $local_data_dir$filenameLocalHistory

    # Copy from local to global dir
    echo "Copying from $local_data_dir to $global_data_dir"
    cp $local_data_dir$filenameLocal $global_data_dir
    cp $local_data_dir$filenameLocalHistory $global_data_dir
    cp $local_data_dir$filenameBadRCUs $global_data_dir
    echo "Copied from $local_data_dir to $global_data_dir"
fi

if [ $SERVICE == "yes" ]
then
    # Show last results on screen
    show_test_result.py -f=$local_data_dir$filenameNow
fi
