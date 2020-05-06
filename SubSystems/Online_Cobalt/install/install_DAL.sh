#!/bin/bash -eu

# We need to be lofarbuild to have the proper writing rights
[ "`whoami`" == "lofarbuild" ]

# Download location for the latest DAL source
DAL_SOURCE="https://github.com/nextgen-astrodata/DAL.git"

# ********************************************
#  Install latest DAL
#
#  into /opt/DAL
# ********************************************
echo "Configuring DAL..."
DALDIR=`mktemp -d`
pushd $DALDIR >/dev/null

echo "  Downloading..."
git clone -q $DAL_SOURCE
cd DAL

echo "  WARNING: Checking out specific revision c60bd6f01fa9f296dcc3e6db835363222038165b for DAL v2.5 (ignoring the new commits for v3.3 for TBB-Alert)..."
git checkout c60bd6f01fa9f296dcc3e6db835363222038165b

echo "  Configuring..."
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=/opt/DAL .. > cmake.log

echo "  Building..."
make -j 8 > make.log

echo "  Testing..."
ctest -j 8 > ctest.log

echo "  Installing..."
make -j 8 install > make_install.log

echo "  Cleaning up..."
popd >/dev/null
rm -rf "$DALDIR"

