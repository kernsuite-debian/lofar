#!/usr/bin/env python3
import os
import sys

from django.core.management import execute_from_command_line

def main(argv):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lofar.triggerservices.restinterface.settings")
    execute_from_command_line(argv)

if __name__ == "__main__":
    main(sys.argv)
