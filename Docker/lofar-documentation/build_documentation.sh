#!/bin/bash
#
# Automates steps to configure and build the LOFAR documentation from within the Docker container
#

LOFAR_BRANCH_MOUNT_DIR=/opt/LOFAR

# We need to have some LOFAR branch mounted, otherwise quit
if [ ! -d "$LOFAR_BRANCH_MOUNT_DIR" ]; then
  echo "No LOFAR branch/tag/trunk mounted at: $LOFAR_BRANCH_MOUNT_DIR"
  echo ""
  echo "Please run the docker container with argument:"
  echo  "-v [PATH_TO_LOFAR_BRANCH_ON_HOST]:/opt/LOFAR/"
  echo ""
  echo "Exiting now"
  exit 1
fi

# Suggest user to make use of the predefined CMake settings based on the hostname passed to the container
HOSTNAME=`hostname`
if [ "lofardocker" != "$HOSTNAME" ]; then
  echo "In order to use the CMake presets from the variants file 'variants.lofar-documentation'"
  echo "run the docker container with the hostname argument:"
  echo "-h lofardocker"
  echo ""
fi

echo "Cleaning up files and folders from any previous built"
rm -rf "$LOFAR_BRANCH_MOUNT_DIR/build/gnucxx11_opt"

echo "Creating the build directory"
mkdir -p "$LOFAR_BRANCH_MOUNT_DIR/build/gnucxx11_opt"

echo "Advancing to the build directory"
cd "$LOFAR_BRANCH_MOUNT_DIR/build/gnucxx11_opt"

echo "Instructing CMake to prepare for building documentation using:"
echo "DOX_SERVER_BASED_SEARCH=$DOX_SERVER_BASED_SEARCH"
echo "DOX_REVISION_SLUG=$DOX_REVISION_SLUG"
cmake -DBUILD_DOCUMENTATION=ON ../..
# Do this twice to get rid of CMakeCache error generated only the first run
cmake -DBUILD_DOCUMENTATION=ON ../..

echo "Instructing CMake to build the documentation"
make doc

