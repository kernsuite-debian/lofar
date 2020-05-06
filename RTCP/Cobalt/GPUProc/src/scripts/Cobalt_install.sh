#!/bin/sh
# Install {RELEASE_NAME}.ztar from the NEXUS onto cbt nodes.
#
# Note: the 'current' symlink still has to be repointed on all cbt nodes to use the new release by default!
#
# $Id$

# location of the file in the NEXUS
if [ "${RELEASE_NAME}" = "" ]; then
  echo "ERROR: RELEASE_NAME is not set or empty. Needed to download archive to install"
  exit 1
fi

FILENAME=Online_Cobalt_${RELEASE_NAME}.ztar

if [[ "${RELEASE_NAME}" == *"Release"* ]]; then
  NEXUS_URL=https://support.astron.nl/nexus/content/repositories/releases/nl/astron/lofar/${RELEASE_NAME}/${FILENAME}
else
  NEXUS_URL=https://support.astron.nl/nexus/content/repositories/branches/nl/astron/lofar/${RELEASE_NAME}/${FILENAME}
fi

# Download archive from NEXUS. -N: clobber existing files
wget -N --tries=3 --no-check-certificate --user=macinstall --password=macinstall "${NEXUS_URL}" -O /tmp/${FILENAME} || exit 1

# The full pathnames are in the tar file, so unpack from root dir.
# -m: don't warn on timestamping /localhome
cd / && tar --no-overwrite-dir -zxvmf /tmp/${FILENAME} || exit 1

# Remove tarball
rm -f /tmp/${FILENAME}

#
# Post-install
#

cd /opt/lofar-versions/${RELEASE_NAME} || exit 1

# Sym link installed var/ to common location.
ln -sfT /localdata/lofar-userdata/var var

# Sym link installed etc/parset-additions.d/override to common location.
ln -sfT /localdata/lofar-userdata/parset-overrides etc/parset-additions.d/override

# Sym link installed var/ to NFS location.
ln -sfT /opt/shared/lofar-userdata nfs


# Set capabilities so our soft real-time programs can elevate prios.
#
# cap_sys_nice: allow real-time priority for threads
# cap_ipc_lock: allow app to lock in memory (prevent swap)
# cap_net_raw:  allow binding sockets to NICs
OUTPUTPROC_CAPABILITIES='cap_sys_nice,cap_ipc_lock'
sudo /sbin/setcap "${OUTPUTPROC_CAPABILITIES}"=ep bin/outputProc || true
sudo /sbin/setcap "${OUTPUTPROC_CAPABILITIES}"=ep bin/TBB_Writer || true
RTCP_CAPABILITIES='cap_net_raw,cap_sys_nice,cap_ipc_lock'
sudo /sbin/setcap "${RTCP_CAPABILITIES}"=ep bin/rtcp

