#!/bin/bash -ex
# LOFAR-Dragnet-activate.sh
#
# LOFAR DRAGNET software activation. Repoint /opt/lofar_versions/current symlink to already deployed LOFAR release.
#
# Preferably run as lofarbuild. It can write in /opt/lofar_versions/, but it also needs to own the symlink.
#
# Jenkins shell command:
# svn export --force https://svn.astron.nl/LOFAR/trunk/SubSystems/Dragnet/scripts/LOFAR-Dragnet-activate.sh && \
#   ./LOFAR-Dragnet-activate.sh "$LOFAR_SVN_TAG" && \
#   rm LOFAR-Dragnet-activate.sh
#
# $Id$

if [ $# -eq 0 ]; then
  echo "Usage: $0 LOFAR_SVN_TAG"
  echo '  LOFAR_SVN_TAG: e.g.: trunk or tags/LOFAR-Release-2_17_5 or just LOFAR-Release-2_17_5'
  exit 1
fi

lofar_svn_tag="$1"
shift

# unload all loaded env modules to avoid accidentally depending on pkgs in PATH, LD_LIBRARY_PATH, ...
module purge || true


# config: version, paths, hostnames
lofar_release=$(echo $lofar_svn_tag | cut -d '/' -f 2)  # select tag or branch name, or trunk
lofar_versions_root=/opt/lofar_versions
prefix=$lofar_versions_root/$lofar_release
nodelist="dragnet dragproc $(seq -s ' ' -f drg%02g 1 23)"

# basic sanity check on selected release name
if [ ! -e "$lofar_versions_root/$lofar_release/lofarinit.sh" ]; then
  echo "Error: selected release is not installed: missing $lofar_versions_root/$lofar_release/lofarinit.sh"
  exit 1
elif [ "$lofar_release" == current ]; then
  echo "Error: 'current' itself is not an acceptable release name to activate, as it refers to the active release"
  exit 1
fi

# repoint 'current' symlink to release version atomically (using mv -T)
# pray it works on every node, else the cluster's LOFAR install ends up in limbo...
declare -a status_arr3
declare arr3_i=0
for host in $nodelist; do
  # Escape double quotes below the following line! And use \ at newline and don't use '#' comments across ssh as lofarbuild uses tcsh...
  ssh -q -o BatchMode=yes -o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no $host "
    hostname && \
    cd $lofar_versions_root && \
    ln -sfT $lofar_release current_tmp && mv -fT current_tmp current && \
    sync
  " >&2 &
  status_arr3[$arr3_i]=$!
  ((arr3_i++)) || true
done
for ((i = 0; i < $arr3_i; i++)); do
  wait ${status_arr3[$i]}
done
