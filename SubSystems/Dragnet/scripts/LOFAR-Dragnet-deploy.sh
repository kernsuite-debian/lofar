#!/bin/bash -ex
# LOFAR-Dragnet-deploy.sh
#
# LOFAR software build and deploy for the LOFAR DRAGNET cluster.
# Does not activate deployed software (i.e. does not repoint 'current' symlink). See LOFAR-Dragnet-activate.sh
#
# Running user (preferably lofarbuild) needs to be able to:
# - scp/ssh without interactivity (set up ssh keys)
# - use setcap(1) (restricted, see /etc/sudoers.d/setcap_cobalt on each node)
# - install new module env file into /etc/modulefiles/lofar/
#
# Jenkins shell command:
# svn export --force https://svn.astron.nl/LOFAR/trunk/SubSystems/Dragnet/scripts/LOFAR-Dragnet-deploy.sh && \
#   ./LOFAR-Dragnet-deploy.sh "$LOFAR_SVN_TAG" && \
#   rm LOFAR-Dragnet-deploy.sh
#
# where $LOFAR_SVN_TAG is set by Jenkins. Examples: trunk or tags/LOFAR-Release-2_17_5 or branches/CEP-Pipeline-Task1234
#
# $Id$

if [ $# -eq 0 ]; then
  echo "Usage: $0 LOFAR_SVN_TAG"
  echo '  LOFAR_SVN_TAG: e.g.: trunk or tags/LOFAR-Release-2_17_5 or branches/CEP-Pipeline-Task1234'
  exit 1
fi

lofar_svn_tag="$1"
shift

# unload all loaded env modules to avoid accidentally depending on pkgs in PATH, LD_LIBRARY_PATH, ...
module purge || true


# config: version, paths, hostnames
lofar_release=$(echo $lofar_svn_tag | cut -d '/' -f 2)  # select tag or branch name, or trunk

lofar_release_tag_prefix=LOFAR-Release-
lofar_version=${lofar_release#$lofar_release_tag_prefix}  # chop off prefix if there
if [ "$lofar_version" == "$lofar_release" ]; then
  unset lofar_version  # no release prefix, so no version nr
else
  lofar_version=$(echo $lofar_version | tr _ . )  # empty or e.g. 2_17_5 -> 2.17.5
fi
echo $lofar_version

lofar_svn_root=https://svn.astron.nl/LOFAR
lofar_versions_root=/opt/lofar_versions
prefix=$lofar_versions_root/$lofar_release
#
# AS: Removed drg10 from nodelist as it is (temporarily) broken!!
#
nodelist="dragnet dragproc $(seq -s ' ' -f drg%02g 1 23 | sed s/drg10//g)"
tmpdir=`mktemp -d 2>/dev/null || mktemp -d -t tempdir`  # GNU/Linux and Mac OS X compat mktemp usage
buildtype=gnucxx11_optarch  # optarch enables -O3 -march=native

pushd "$tmpdir"

# check out release. Don't svn export LOFAR if you care about version strings, incl what goes into data products.
svn checkout $lofar_svn_root/$lofar_svn_tag LOFAR > /dev/null

# build, install into DESTDIR, and create deploy archive
mkdir -p $buildtype && cd $buildtype
cmake -DBUILD_PACKAGES=Dragnet -DCMAKE_INSTALL_PREFIX=$prefix ../LOFAR
make -j 7 install DESTDIR="$tmpdir"/destdir
cd ../destdir
archive=$lofar_release-Dragnet.tgz
tar zcf $archive *  # whole $prefix path ends up in archive entries

# create environment module file if it is a LOFAR-Release-*
envmodfilename=$lofar_version
if [ -n "$lofar_version" ]; then
  echo '#%Module 1.0' >> $envmodfilename
  echo 'module-whatis           "Adds the ASTRON LOFAR tree (NDPPP, BBS, awimager, pybdsm, ...) release '$lofar_version' to your environment (do not mix with sourcing lofarinit.sh)"' >> $envmodfilename
  echo 'conflict                lofar' >> $envmodfilename
  echo 'prepend-path            PATH            '$prefix'/bin:'$prefix'/sbin' >> $envmodfilename
  echo 'prepend-path            LD_LIBRARY_PATH '$prefix'/lib64' >> $envmodfilename
  echo 'prepend-path            PYTHONPATH      '$prefix'/lib64/python2.7/site-packages' >> $envmodfilename
  echo 'setenv                  LOFARENV        PRODUCTION' >> $envmodfilename
  echo 'setenv                  LOFARROOT       '$prefix >> $envmodfilename
  echo '#setenv                  LOFARDATAROOT   /opt/lofar/data' >> $envmodfilename
fi

# parallel copy of module env file (if any) and archive across cluster nodes
declare -a status_arr1
declare arr1_i=0
for host in $nodelist; do
  scp -p -q -o BatchMode=yes -o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no $envmodfilename $archive $host:$lofar_versions_root/ &
  status_arr1[$arr1_i]=$!
  ((arr1_i++)) || true
done
for ((i = 0; i < $arr1_i; i++)); do
  wait ${status_arr1[$i]}
done

# Unpack and set up across cluster (requires $prefix and /etc/modulefiles/lofar/ to be writable).
# The archived files all have full pathname, so unpack from root dir, but avoid attempted metadata changes on /opt.
# Need to replace created var/ subdirs by symlink to common var/ dir.
# The sudo setcap cmds reqs a sudoers.d/ file in place to allow lofarbuild to do this without auth.
declare -a status_arr2
declare arr2_i=0
for host in $nodelist; do
  # Escape double quotes below the following line! And use \ at newline and don't use '#' comments across ssh as lofarbuild uses tcsh...
  ssh -tt -q -o BatchMode=yes -o NoHostAuthenticationForLocalhost=yes -o StrictHostKeyChecking=no $host "
    hostname && \
    cd $lofar_versions_root && \
    rm -rf -- $lofar_release && \
    cd / && tar -x -z --no-overwrite-dir -f $lofar_versions_root/$archive && \
    rm -rf -- $prefix/var && \
    ln -sfT /home/lofarsys/lofar/var $prefix/var && \
    rm -- \"$lofar_versions_root/$archive\" && \
    cd $lofar_versions_root && \
    ( [ -z \"$envmodfilename\" ] || mv $envmodfilename /etc/modulefiles/lofar/ ) && \
    sudo -n /sbin/setcap cap_net_raw,cap_sys_nice,cap_sys_resource,cap_ipc_lock=ep $prefix/bin/rtcp && \
    sudo -n /sbin/setcap cap_net_raw,cap_sys_nice,cap_sys_resource,cap_ipc_lock=ep $prefix/bin/outputProc && \
    sudo -n /sbin/setcap cap_net_raw,cap_sys_nice,cap_sys_resource,cap_ipc_lock=ep $prefix/bin/TBB_Writer && \
    sync
  " >&2 &
  status_arr2[$arr2_i]=$!
  ((arr2_i++)) || true
done
for ((i = 0; i < $arr2_i; i++)); do
  wait ${status_arr2[$i]}
done

popd  # move away from dir that we are about to remove
rm -rf -- "$tmpdir"
