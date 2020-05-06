#!/bin/bash

GET_VERSION=0
SET_VERSION=""
LIST_VERSIONS=0

function error() {
  echo "$@" >&2
  exit 1
}

function usage() {
  echo "$0 [-l] [-g] [-s VERSION]"
  echo ""
  echo "  -l            List available Cobalt versions"
  echo "  -g            Get active Cobalt version"
  echo "  -s VERSION    Set active Cobalt version"
  exit 1
}

while getopts "hgls:" opt; do
  case $opt in
    h)  usage
        ;;
    g)  GET_VERSION=1
        ;;
    l)  LIST_VERSIONS=1
        ;;
    s)  SET_VERSION="$OPTARG"
        ;;
    \?) error "Invalid option: -$OPTARG"
        ;;
    :)  error "Option requires an argument: -$OPTARG"
        ;;
  esac
done
[ $OPTIND -eq 1 ] && usage

COBALT_VERSIONS_DIR=/opt/lofar-versions

[ -d "$COBALT_VERSIONS_DIR" ] || error "Directory not found: $COBALT_VERSIONS_DIR"

# List Cobalt versions
if [ $LIST_VERSIONS -eq 1 ]; then
  ls -1 $COBALT_VERSIONS_DIR
fi

CURRENT_VERSION=`readlink -f /opt/lofar | awk -F/ '{ print $NF; }'`

# Get current Cobalt version
if [ $GET_VERSION -eq 1 ]; then
  echo "$CURRENT_VERSION"
fi

# Set current Cobalt version
if [ -n "$SET_VERSION" ]; then
  echo "Switching Cobalt to $SET_VERSION"

  function set_version {
    VERSION="$1"

    # Don't create loops
    [ $VERSION == current ] && return 1

    # Don't activate non-existing releases
    [ -d "${COBALT_VERSIONS_DIR}/${VERSION}" ] || return 1

    # Move symlink, activating selected version
    clush -g all -S ln -sfT "${COBALT_VERSIONS_DIR}/${VERSION}" "${COBALT_VERSIONS_DIR}/current" || return 1

    return 0
  }

  if ! set_version "$SET_VERSION"; then
    echo "------------------------------------------------------------------------------"
    echo "ERROR Switching to $SET_VERSION. Switching back to $CURRENT_VERSION"
    echo "------------------------------------------------------------------------------"

    set_version "$CURRENT_VERSION"
  fi
fi

