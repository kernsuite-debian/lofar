#!/usr/bin/env bash

# Configure user
if [ -z "${USER}" ]; then
  export USER=${UID}
fi

# Create home directory
if [ -z "${HOME}" ]; then
  export HOME=/home/${USER}
  mkdir -p $HOME && cd $HOME
fi

# Set the environment
[ -e /opt/bashrc ] && source /opt/bashrc

# Run the requested command
if [ -z "$*" ]; then
  exec /bin/bash
else
  exec "$@"
fi
