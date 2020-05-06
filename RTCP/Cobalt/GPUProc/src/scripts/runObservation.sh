#!/bin/bash
#
# Runs an observation, in the foreground, logging to stdout/stderr.
#
# This script takes care of running all the commands surrounding mpirun.sh,
# based on the given parset.
#
# $Id$


########  Functions  ########

source cobalt_functions.sh

function error {
  echo -e "$@" >&2
  sendback_state 1
  exit 1
}

function usage {
  echo -e \
    "\nUsage: $0 [-A] [-B] [-C] [-F] [-P pidfile] [-l nprocs] [-p] [-o KEY=VALUE] [-x KEY=VALUE] PARSET"\
    "\n"\
    "\n  Run the observation specified by PARSET"\
    "\n"\
    "\n    -A: do NOT augment parset"\
    "\n    -B: do NOT add broken antenna information"\
    "\n    -C: run with check tool specified in environment variable"\
    "LOFAR_CHECKTOOL"\
    "\n    -F: do NOT send data points to a PVSS gateway"\
    "\n    -P: create PID file"\
    "\n    -d: dummy run: don't execute anything"\
    "\n    -l: run solely on localhost using 'nprocs' MPI processes (isolated test)"\
    "\n    -p: enable profiling" \
    "\n    -o: add option KEY=VALUE to the parset" \
    "\n    -x: propagate environment variable KEY=VALUE"\
    "\n" >&2
  exit 1
}

# Send the result state back to LOFAR (MAC, MoM)
#
# to report success:
#   sendback_status 0
# to report failure:
#   sendback_status 1
function sendback_state {
  OBSRESULT="$1"

  if [ $OBSRESULT -eq 0 ]
  then
    echo "[cobalt] Signalling success"
    SUCCESS=1
  else
    # ***** Observation or sending feedback failed for some reason
    echo "[cobalt] Signalling failure"
    SUCCESS=0
  fi

  send_state "$PARSET" $SUCCESS
}

#############################

echo "Called as: $0 $@"

# ******************************
# Set default options
# ******************************

# Provide data points to PVSS?
STATUS_FEEDBACK=1

# Augment the parset with etc/parset-additions.d/* ?
AUGMENT_PARSET=1

# Extra parset keys to add
EXTRA_PARSET_KEYS=""

# Whether to execute anything
DUMMY_RUN=false

# File to write PID to
PIDFILE=""

# Force running on localhost instead of the hosts specified
# in the parset?
FORCE_LOCALHOST=0
NRPROCS_LOCALHOST=0

# Add broken antenna information?
ADD_BROKENANTENNAINFO=1

# Parameters to pass to mpirun
MPIRUN_PARAMS=""

# Pipe through which to send commands to the run
COMMAND_PIPE=""

# Parameters to pass to rtcp
RTCP_PARAMS=""

# ******************************
# Parse command-line options
# ******************************
while getopts ":ABCFP:dl:o:px:c:" opt; do
  case $opt in
      A)  AUGMENT_PARSET=0
          ;;
      B)  ADD_BROKENANTENNAINFO=0
          ;;
      C)  CHECK_TOOL="$LOFAR_CHECKTOOL"
          ;;
      F)  STATUS_FEEDBACK=0
          ;;
      P)  PIDFILE="$OPTARG"
          ;;
      c)  COMMAND_PIPE="$OPTARG"
          ;;
      d)  DUMMY_RUN=true
          ;;
      l)  FORCE_LOCALHOST=1
          NRPROCS_LOCALHOST=$OPTARG
          ;;
      o)  EXTRA_PARSET_KEYS="${EXTRA_PARSET_KEYS}${OPTARG}\n"
          ;;
      p)  RTCP_PARAMS="$RTCP_PARAMS -p"
          ;;
      x)  MPIRUN_PARAMS="-x $OPTARG"
          ;;
      \?) echo "Invalid option: -$OPTARG" >&2
          exit 1
          ;;
      :)  echo "Option requires an argument: -$OPTARG" >&2
          exit 1
          ;;
  esac
done

# Remove parsed options
shift $((OPTIND-1))

# Obtain parset parameter
PARSET="$1"

# Show usage if no parset was provided
[ -n "$PARSET" ] || usage

# Check if LOFARROOT is set.
[ -n "$LOFARROOT" ] || error "[cobalt] LOFARROOT is not set!"
echo "[cobalt] LOFARROOT = $LOFARROOT"

# ******************************
# Preprocess: initialise
# ******************************

# Write PID if requested
if [ "$PIDFILE" != "" ]
then
  echo $$ > "$PIDFILE"
fi

# Test the -k option of timeout(1). It only appeared since GNU coreutils 8.5 (fails on DAS-4).
timeout -k2 1 /bin/true 2> /dev/null && KILLOPT=-k2

# Read parset
[ -f "$PARSET" -a -r "$PARSET" ] || error "[parset] Cannot read: $PARSET"

OBSID=`getkey Observation.ObsID`
echo "[cobalt] ObsID = $OBSID"

PROJECT=`getkey Observation.Campaign.name`
echo "[cobalt] Project = $PROJECT"

# Remove stale feedback file (useful for testing)
FEEDBACK_FILE=$LOFARROOT/var/run/Observation${OBSID}_feedback
rm -f $FEEDBACK_FILE

# ******************************
# Preprocess: augment parset
# ******************************

if [ "$AUGMENT_PARSET" -eq "1" ]
then
  AUGMENTED_PARSET=$LOFARROOT/nfs/parset/rtcp-$OBSID.parset

  # Add static keys
  # Ignore sneaky .cobalt/ parset overrides in production (lofarsys).
  # Note: If you want such an override anyway, do it in your own account.
  DOT_COBALT_DEFAULT=$HOME/.cobalt/default/*.parset
  DOT_COBALT_OVERRIDE=$HOME/.cobalt/override/*.parset
  if [ "$USER" == "lofarsys" ]; then
    ls -U -- $DOT_COBALT_DEFAULT >/dev/null 2>&1 && echo "[parset] WARN: ignoring augmentation parset(s) $DOT_COBALT_DEFAULT" >&2
    ls -U -- $DOT_COBALT_OVERRIDE >/dev/null 2>&1 && echo "[parset] WARN: ignoring augmentation parset(s) $DOT_COBALT_OVERRIDE" >&2
    unset DOT_COBALT_DEFAULT DOT_COBALT_OVERRIDE
  fi

  # Avoid passing on "*" if it matches nothing. Restore afterwards.
  nullglob_state=`shopt -p nullglob`
  shopt -s nullglob
  for f in $LOFARROOT/etc/parset-additions.d/default/*.parset \
      $LOFARROOT/etc/parset-additions.d/default/*.$PROJECT \
      $LOFARROOT/etc/parset-additions.d/default/*.$OBSID \
      $DOT_COBALT_DEFAULT \
      $PARSET \
      $LOFARROOT/etc/parset-additions.d/override/*.parset \
      $LOFARROOT/etc/parset-additions.d/override/*.$PROJECT \
      $LOFARROOT/etc/parset-additions.d/override/*.$OBSID \
      $DOT_COBALT_OVERRIDE;
  do
      cat $f
      echo "" # force newline in case the file does not end in one
  done > $AUGMENTED_PARSET || error "[parset] Could not create $AUGMENTED_PARSET"
  eval $nullglob_state

  # Use the new one from now on
  PARSET="$AUGMENTED_PARSET"

  # If we force localhost, we need to remove the node list, or the first one will be used
  # Also set all other location relevant keys to a localhost value
  if [ "$FORCE_LOCALHOST" -eq "1" ]
  then
    setkey Cobalt.Nodes                               []

    setkey Cobalt.OutputProc.userName                 "$USER"
    setkey Cobalt.OutputProc.executable               "$LOFARROOT/bin/outputProc"
    setkey Cobalt.OutputProc.StaticMetaDataDirectory  "$LOFARROOT/etc"
    setkey Cobalt.FinalMetaDataGatherer.database.host localhost
    setkey Cobalt.PVSSGateway.host                    ""
    setkey Observation.Cluster.ProcessingCluster.clusterName ""
    setkey Observation.Cluster.ProcessingCluster.clusterName "localhost"
    setkey Observation.DataProducts.Output_Correlated.storageClusterName       "localhost"
    setkey Observation.DataProducts.Output_CoherentStokes.storageClusterName   "localhost"
    setkey Observation.DataProducts.Output_IncoherentStokes.storageClusterName "localhost"

    # Redirect UDP/TCP input streams to any interface on the local machine
    sed 's/udp:[^:]*:/udp:0:/g' -i $PARSET
    sed 's/tcp:[^:]*:/tcp:0:/g' -i $PARSET
  fi

  if [ "$ADD_BROKENANTENNAINFO" -eq "0" ]
  then
    setkey Cobalt.FinalMetaDataGatherer.enabled       false
  fi

  if [ "$STATUS_FEEDBACK" -eq "0" ]
  then
    setkey Cobalt.PVSSGateway.host                    ""
  fi

  # Add extra keys specified on the command line
  echo -e "$EXTRA_PARSET_KEYS" >> $PARSET
fi

# Create the command pipe to control the run
if [ -n "$COMMAND_PIPE" ]; then
  COMMAND_HOST=`getCobaltHosts -C $PARSET`
  echo "[cobalt] Create command pipe $COMMAND_PIPE on host $COMMAND_HOST"

  timeout 60s ssh $COMMAND_HOST "[ -e $COMMAND_PIPE ] && rm -f $COMMAND_PIPE"
  timeout 60s ssh $COMMAND_HOST "mkfifo -m 0660 $COMMAND_PIPE"

  # Instruct rtcp where to look
  echo -e "Cobalt.commandStream=file:$COMMAND_PIPE" >> $PARSET
fi

# ************************************
# Start outputProcs on receiving nodes
# ***********************************
# Get parameters from the parset
SSH_USER_NAME=$(getkey Cobalt.OutputProc.userName $USER)
SSH_PUBLIC_KEY=$(getkey Cobalt.OutputProc.sshPublicKey)
SSH_PRIVATE_KEY=$(getkey Cobalt.OutputProc.sshPrivateKey)
OBSERVATIONID=$(getkey Observation.ObsID 0)

read_cluster_model

# Determine list of outputProc hosts for various purposes
if $SLURM; then
  # TODO: Start SLURM job, wait for resources, record node list
  echo "ERROR: SLURM resource allocation is not supported"
  exit 1

  # Allocate resources
  # TODO: Start outputProc here
  ssh -o StrictHostKeyChecking=no $HEADNODE srun -N $NRCOMPUTENODES -c 1 --job-name=$OBSID bash -c 'while sleep 1; do :; done' &

  # Wait for allocation
  while [ "`ssh -o StrictHostKeyChecking=no $HEADNODE sacct --starttime=now --noheader --parsable2 --format=state --name=$OBSID | tail -n 1`" != "RUNNING" ]; do sleep 1; done

  # Obtain node list
  NODE_LIST="`ssh -o StrictHostKeyChecking=no $HEADNODE sacct --starttime=now --noheader --parsable2 --format=nodelist --name=$OBSID | tail -n 1`"

  # Expand node list into something usable
  # TODO: move ".cep4" to cluster model
  NODE_LIST="`ssh -o StrictHostKeyChecking=no $HEADNODE scontrol show hostnames $NODE_LISTi | awk '{ print $1 ".cep4"; }'`"
else
  # Derive host list from parset
  NODE_LIST=$(getCobaltHosts -O $PARSET)
fi

# Replace any cluster-name place holders in the locations keys
if $GLOBALFS; then
  if $SLURM; then
    POSSIBLE_NODES="$NODE_LIST"
  else
    POSSIBLE_NODES="$COMPUTENODES"
  fi

  # Update locations in parset
  mv -fT "$PARSET" "$PARSET.generate_globalfs"

  generate_globalfs_locations.py --cluster "$CLUSTER_NAME" --hosts "$POSSIBLE_NODES" < "$PARSET.generate_globalfs" > "$PARSET"

  # Derive updated host list from parset
  NODE_LIST=$(getCobaltHosts -O $PARSET)
fi

echo "[outputProc] Hosts: $NODE_LIST"

# If parameters are found in the parset create a key_string for ssh command
if [ "$SSH_PRIVATE_KEY" != "" ] 
then
  # Use -i to signal usage of the specific key
  KEY_STRING="-i $SSH_PRIVATE_KEY"   
elif [ "$SSH_PUBLIC_KEY" != "" ]
then
  KEY_STRING="-i $SSH_PUBLIC_KEY"
fi

# test the connection with local host: minimal test for valid credentials
ssh -o StrictHostKeyChecking=no -l $SSH_USER_NAME $KEY_STRING "localhost" "/bin/true" || error "[cobalt] Failed to ssh to localhost"

# Create a helper function for delete child processes and
# a file containing the PID of these processes
PID_LIST_FILE="$LOFARROOT/var/run/outputProc-$OBSERVATIONID.pids"

function clean_up_temp_files {
  echo "[children] Removing pid file"
  rm -f $PID_LIST_FILE

  if [ -n "$PIDFILE" ]; then
    echo "[cobalt] Removing pid file"
    rm -f $PIDFILE
  fi

  if [ -n "$COMMAND_PIPE" ]; then
    echo "[cobalt] Removing command pipe"
    rm -f $COMMAND_PIPE
  fi
}

# Function clean_up will clean op all PID in the
# PID_LIST_FILE and the seperately supplied additional list of PIDs
# in argument $2
# First using SIGTERM and then with a kill -9
# It will then exit with the state suplied in argument $1
function clean_up { 
  EXIT_STATE=$1
  PID_LIST=$2

  if $SLURM; then
    echo "[children] Cancelling SLURM allocation"
    ssh -o StrictHostKeyChecking=no $HEADNODE scancel --jobname=$OBSID
  fi
  
  echo "[children] Sending SIGTERM" 
  # THe kill statements might be called with an empty argument. This will 
  # result in an exit state 1. But the error is redirected to dev/null.
  kill $(cat $PID_LIST_FILE)  2> /dev/null
  kill $PID_LIST              2> /dev/null 
  
  echo "[children] Waiting 2 seconds for soft shutdown"
  sleep 2
  
  echo "[children] Sending SIGKILL"
  kill -9 $(cat $PID_LIST_FILE) 2> /dev/null
  kill -9 $PID_LIST             2> /dev/null

  clean_up_temp_files
  
  exit $EXIT_STATE 
}

# We can now create a trap for signals, no arguments so only
# clean of the PID file list the list of sub shells
trap 'clean_up 1' SIGTERM SIGINT SIGQUIT SIGHUP EXIT

# Start output procs in a seperate function
# Save file for started child processes
# Use helper program to get the list of hosts from parset
echo "[outputProc] pid file = $PID_LIST_FILE"
touch $PID_LIST_FILE

# Construct full command line for outputProc
OUTPUTPROC_CMDLINE="source $OUTPUTPROC_ROOT/lofarinit.sh; export QUEUE_PREFIX=$QUEUE_PREFIX LOFARENV=$LOFARENV; numactl --cpunodebind=0 --preferred=0 $OUTPUTPROC_ROOT/bin/outputProc $OBSERVATIONID"

# Wrap command line with Docker if required
if $DOCKER; then
  TAG="`echo '${LOFAR_TAG}' | docker-template`"

  # "echo 950000 > /sys/fs/cgroup/cpu/cpu.rt_runtime_us" is needed to configure the real-time scheduler for this cgroup
  # --cpu-shares=24576 (=24*1024) provides this process with as much share of the CPU as 24 other containers (note: CEP4 has 24 cores/node)
  OUTPUTPROC_CMDLINE="docker-run-slurm.sh --rm --cpu-shares=24576 --cap-add=sys_nice --cap-add=sys_admin -u `id -u $SSH_USER_NAME` --net=host -v $GLOBALFS_DIR:$GLOBALFS_DIR lofar-outputproc:$TAG bash -c \"sudo echo 950000 > /sys/fs/cgroup/cpu/cpu.rt_runtime_us; $OUTPUTPROC_CMDLINE\""
fi

echo "[outputProc] command line = $OUTPUTPROC_CMDLINE"

if ! $DUMMY_RUN; then
  if $SLURM; then
    # The nodes we need (and can use) are part of this job
    COMMAND="srun -N $SLURM_JOB_NUM_NODES -J $OBSID.outputproc $OUTPUTPROC_CMDLINE"
    echo "[outputProc] Starting $COMMAND"

    $COMMAND &
    PID=$!

    echo -n "$PID " >> $PID_LIST_FILE  # Save the pid for cleanup
  else
    for HOST in $NODE_LIST
    do
      COMMAND="ssh -tt -o StrictHostKeyChecking=no -l $SSH_USER_NAME $KEY_STRING $SSH_USER_NAME@$HOST $OUTPUTPROC_CMDLINE"
      echo "[outputProc] Starting $COMMAND"
      
      $COMMAND &
      PID=$!
      
      echo -n "$PID " >> $PID_LIST_FILE  # Save the pid for cleanup
    done
  fi
fi

# ******************************
# Distribute parset to cbtXXX
# ******************************

# Determine node list to run on
HOSTS=`mpi_node_list -n "$PARSET"`

if [ -z "$HOSTS" ]; then
  HOSTS=`python -c 'print(",".join(["localhost"]*'$NRPROCS_LOCALHOST'))'`
fi

echo "[cobalt] Hosts = $HOSTS"

# ************************************
# Start rtcp 
# ***********************************

echo "[cobalt] parset = $PARSET"

# Run in the background to allow signals to propagate
#
# -x LOFARROOT    Propagate $LOFARROOT for rtcp to find GPU kernels, config files, etc.
# -x QUEUE_PREFIX Propagate $QUEUE_PREFIX for test-specific interaction over the message bus
# -H              The host list to run on, derived earlier.
if $DUMMY_RUN; then
  # Just return success
  true &
else
  mpirun.sh -x LOFARROOT="$LOFARROOT" \
            -x QUEUE_PREFIX="$QUEUE_PREFIX" \
            -x LOFARENV="$LOFARENV" \
            -x OMP_PROC_BIND=FALSE \
            -H "$HOSTS" \
            $MPIRUN_PARAMS \
            $CHECK_TOOL \
            `which rtcp` $RTCP_PARAMS "$PARSET" &
fi
PID=$!

# Propagate SIGTERM
trap "echo '[cobalt] runObservation.sh: Received signal.'; clean_up 1 $PID" SIGTERM SIGINT SIGQUIT SIGHUP EXIT

# Wait for $COMMAND to finish. We use 'wait' because it will exit immediately if it
# receives a signal.
#
# Return code:
#   signal:    >128
#   no signal: return code of mpirun.sh
wait $PID
OBSRESULT=$?

echo "[cobalt] Exit code of observation: $OBSRESULT"

# Return codes of rtcp:
#  0 = success
#  1 = rtcp detected failure
# >1 = crash, but possibly at teardown after a succesful observation
if [ $OBSRESULT -gt 1 -a -s $FEEDBACK_FILE ]
then
  # There is a feedback file! Consider the observation as succesful,
  # to prevent crashes in the tear down from ruining an otherwise
  # perfectly good observation.
  #
  # Note that we might miss failures detected by rtcp, such as
  # missing final meta data!
  echo "[cobalt] Found feed-back file $FEEDBACK_FILE, considering the observation succesful."

  OBSRESULT=0
fi

# ******************************
# Post-process the observation
# ******************************

sendback_state "$OBSRESULT"

# clean up outputProc children
echo "[outputProc] Waiting up to 120 seconds for normal end"
#    Set trap to kill the sleep in case of signals                    save the pid of sleep
( trap 'kill $SLEEP_PID' SIGTERM SIGINT SIGQUIT SIGHUP; sleep 120 & SLEEP_PID=$!; wait $SLEEP_PID; echo '[outputProc] Killing'; clean_up 0 ) & 
KILLER_PID=$!

# Waiting for the child processes to finish
LIST_OF_PIDS_TO_WAIT_FOR=$(cat $PID_LIST_FILE)
if [ "$LIST_OF_PIDS_TO_WAIT_FOR" != "" ] # if there are outputProc pid working
then
  echo "[outputProc] Waiting..."
  wait $(cat $PID_LIST_FILE)        2> /dev/null
fi

# All OutputProcs are now killed, cleanup of the killer
kill $KILLER_PID                  2> /dev/null

# Cleanup our littering
clean_up_temp_files

# Cleanup exit traps to prevent unnecessary cleanup
trap - EXIT

# Our exit code is that of the observation
# In production this script is started in the background, so the exit code is for tests.
exit $OBSRESULT

