#!/usr/bin/env python3

import time
import sys

output = ' '.join(sys.argv[1:])

for ch in output:
    sys.stdout.write(ch)
    time.sleep(0.2)
    sys.stdout.flush()
