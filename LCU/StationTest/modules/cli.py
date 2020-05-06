"""Command line interface access
"""

################################################################################
# System imports
import subprocess

################################################################################
# Functions

def command(arg, p=False):
  if p:
    print(arg)
  return subprocess.getoutput(arg)
