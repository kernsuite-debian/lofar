
function addlogprefix {
  ME="`basename -- "$0" .sh`@`hostname`"
  while read LINE
  do
    echo "$ME" "`date "+%F %T.%3N"`" "$LINE"
  done
}

#
# The following functions assume that $PARSET is set.
#

function getkey {
  KEY=$1
  DEFAULT=$2

  # grab the last key matching "^$KEY=", ignoring spaces.
  VALUE=`<$PARSET perl -ne '/^'$KEY'\s*=\s*"?(.*?)"?\s*$/ || next; print "$1\n";' | tail -n 1`

  if [ "$VALUE" == "" ]
  then
    echo "$DEFAULT"
  else
    echo "$VALUE"
  fi
}

function setkey {
  KEY=$1
  VAL=$2

  # In case already there, comment all out to avoid stale warnings. Then append.
  KEYESC=`echo "$KEY" | sed -r -e "s/([\.[])/\\\\\\\\\1/g"`  # escape '.' '[' chars in keys with enough '\'
  sed -i --follow-symlinks -r -e "s/^([[:blank:]]*$KEYESC[[:blank:]]*=)/#\1/g" "$PARSET"
  echo "$KEY = $VAL" >> "$PARSET"
}

COBALT_DATAPRODUCTS="Correlated CoherentStokes IncoherentStokes RSPRaw"

function read_cluster_model {
  # HACK: Search for first cluster, and assume they're all the same. We support only output
  # to a single cluster for now.
  for DP in ${COBALT_DATAPRODUCTS}; do
    CLUSTER_NAME=$(getkey Observation.DataProducts.Output_${DP}.storageClusterName "")
    if [ -n "${CLUSTER_NAME}" ]; then
      break
    fi
  done

  # Hack to derive required properties (cluster model) from cluster name.
  case "${CLUSTER_NAME}" in
    CEP4)
      HEADNODE=head.cep4.control.lofar
      SLURM_PARTITION=cpu
      SLURM_RESERVATION=cobalt
      RESVCACHE=$LOFARROOT/var/run/slurmresv.cache
      COMPCACHE=$LOFARROOT/var/run/compnodes.cache

      # Get the reserved CEP4 nodes for output writing. Try three methods in order of precedence: 
      # 1. Get nodes from the cobalt slurm reservation (must have state active)
      # 2. Read a cache file with the node list
      # 3. Default to a particular set of nodes
      echo "Reading the slurm '$SLURM_RESERVATION' reservation.."
      RESVNODES=$(ssh $HEADNODE scontrol show res -o $SLURM_RESERVATION  | \
                  perl -n -e 'm/Nodes=(.*?) .*State=ACTIVE/ ? print STDOUT $1 : die "WARNING: No active reservation found\n"')
      if [ -n "$RESVNODES" ]; then
        # save in cache
        cat <<-CAT > $RESVCACHE 
		echo "Cache created at $(date)"
		RESVNODES="$RESVNODES"
	CAT
      elif [ -s $RESVCACHE ]; then
        echo "Reading the cache file '$RESVCACHE'"
        source $RESVCACHE
      else
        echo "WARNING: No reserved nodes and no cache file found, using defaults"
        RESVNODES="cpu[40-44]"
      fi
      echo "Reserved nodes: $RESVNODES"

      # Checking online status: try three methods in order of precedence: 
      # 1. Check slurm for the node status (sinfo)
      # 2. Read a cache file with the node list
      # 3. Default to a particular set of nodes
      echo "Checking online status"
      SINFO_FLAGS="--responding --states=idle,mixed,alloc,reserved -n $RESVNODES"
      COMPUTENODES="$(ssh $HEADNODE sinfo --format=%n.cep4.infiniband.lofar,%T --noheader --sort=N $SINFO_FLAGS | fgrep -v ,draining | cut -f1 -d,)"
      if [ -n "$COMPUTENODES" ]; then
        # save in cache
        cat <<-CAT > $COMPCACHE 
		echo "Cache created at $(date)"
		COMPUTENODES="$COMPUTENODES"
	CAT
      elif [ -s $COMPCACHE ]; then
        echo "Reading the cache file '$COMPCACHE'"
        source $COMPCACHE
      else
        echo "WARNING: No active nodes and no cache file found, using defaults"
        COMPUTENODES="`seq -f "cpu%02.0f.cep4.infiniband.lofar" 40 44`"
      fi
      echo -e "Nodes used for output writing:\n${COMPUTENODES}"

      GLOBALFS=true
      GLOBALFS_DIR=/data
      SLURM=false    # Don't use SLURM for now, let's get it working without it first
      DOCKER=false   # disabled as outputproc is too slow on docker 1.9.1 (#9522)
      OUTPUTPROC_ROOT="`echo '/opt/outputproc-${LOFAR_TAG}' | docker-template`"
      ;;
    DRAGNET)
      HEADNODE=dragnet.control.lofar
      SLURM_PARTITION=lofarobs  # NOTE: sinfo (without -a) only displays this partition for members of the lofarsys group (+ slurm,root)
      COMPUTENODES="`ssh $HEADNODE sinfo --responding --states=idle,mixed,alloc --format=%n-ib.dragnet.infiniband.lofar,%T --noheader --partition=$SLURM_PARTITION --sort=N | fgrep -v ,draining | cut -f1 -d,`"
      if [ -z "$COMPUTENODES" ]; then
        echo "ERROR: Could not obtain list of available DRAGNET nodes. Defaulting to drg01 - drg23 -ib.dragnet.infiniband.lofar"
        COMPUTENODES="`seq -f "drg%02.0f-ib.dragnet.infiniband.lofar" 1 23`"
      fi
      COMPUTENODES=$(echo $COMPUTENODES | sed -e s/dragproc-ib.dragnet.infiniband.lofar/dragproc-10g.online.lofar/g)  # dragproc has no infiniband i/f, so use 10g

      #SLURM=true
      SLURM=false # Don't use SLURM for now, let's get it working without it first
      GLOBALFS=false
      DOCKER=false

      #OUTPUTPROC_ROOT="/opt/lofar_versions/${LOFAR_TAG}"  # allows testing releases without disturbing operations, but requires good LOFAR version sync between COBALT and DRAGNET
      OUTPUTPROC_ROOT="/opt/lofar"
      ;;
    localhost)
      # For test and development
      COMPUTENODES=localhost

      SLURM=false
      GLOBALFS=false
      DOCKER=false

      OUTPUTPROC_ROOT="$LOFARROOT"
      ;;
    *)
      echo "ERROR: unknown cluster name from parset storageClusterName key(s): $CLUSTER_NAME"
      exit 1
      ;;
  esac

  NRCOMPUTENODES=`echo $COMPUTENODES | wc -w`
}
