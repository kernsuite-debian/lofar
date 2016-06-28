#!/bin/bash -e

# Entry script from MAC on non-CEP2 clusters (CEP2 uses startPython.sh).
#
# The following chain is executed:
#
#   setStatus(STARTED)
#   getParset()
#   (execute pipeline as specified in parset)
#   setStatus(COMPLETING)
#   setStatus(FINISHED)
#
# Syntax:
#
#   runPipeline.sh -o <obsid> || pipelineAborted.sh -o <obsid>

# ======= Defaults

# Obs ID
OBSID=

# Parset (will be requested if not set)
PARSET=

# Location of pipeline-framework configuration file
PIPELINE_CONFIG=$LOFARROOT/share/pipeline/pipeline.cfg

# ======= Parse command-line parameters

function usage() {
  echo "$0 -o OBSID [options]"
  echo ""
  echo "  -o OBSID           Task identifier"
  echo "  -c pipeline.cfg    Override pipeline configuration file (default: $PIPELINE_CONFIG)"
  echo "  -p pipeline.parset Provide parset (default: request through QPID)"
  exit 1
}

while getopts "ho:c:p:" opt; do
  case $opt in
    h)  usage
        ;;
    o)  OBSID="$OPTARG"
        ;;
    c)  PIPELINE_CONFIG="$OPTARG"
        ;;
    p)  PARSET="$OPTARG"
        ;;
    \?) error "Invalid option: -$OPTARG"
        ;;
    :)  error "Option requires an argument: -$OPTARG"
        ;;
  esac
done
[ -z "$OBSID" ] && usage

# ======= Init

if [ -z "$PARSET" ]; then
  # Fetch parset
  PARSET=${LOFARROOT}/var/run/Observation${OBSID}.parset
  getOTDBParset -o $OBSID >$PARSET
fi

# ======= Run

# Fetch parameters from parset
PROGRAM_NAME=$(getparsetvalue $PARSET "ObsSW.Observation.ObservationControl.PythonControl.pythonProgram")

# Run pipeline
OPTIONS=" -d -c $PIPELINE_CONFIG"
  
# Set up the environment (information to propagate to the node scripts for monitoring and logging)
export LOFAR_OBSID="$OBSID"

# Start the Python program
echo "**** $(date) ****"
echo "Executing: ${PROGRAM_NAME} ${OPTIONS} ${PARSET}"

# Run and propagate SIGTERM, SIGINT
exec ${PROGRAM_NAME} ${OPTIONS} ${PARSET}
