#!/bin/bash -e

if [ $# -eq 1 ]; then
    VERSION=$1
else
    echo
    echo "usage: $0 <version>"
    echo 
    echo "example:"
    echo " $ $0 1.10.0"
    echo
    exit 1
fi

LOFAR_TAG=`echo ${VERSION} | tr . _`
svn checkout --depth=files https://svn.astron.nl/LOFAR/tags/LOFAR-Release-${LOFAR_TAG} lofar-${VERSION}
cd lofar-${VERSION}
svn update --depth=infinity CMake
BUILD_DIR=../lofar-${VERSION}-build/gnu_opt
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
cmake -DBUILD_PACKAGES=Offline -DUSE_OPENMP=ON ../../lofar-${VERSION}
cd ../..
tar jcf lofar-${VERSION}.tar.bz2 lofar-${VERSION} --exclude .svn
