# Backward compatibility, so that import lofar.bdsm will still work

import sys
import bdsf

sys.modules[__name__] = sys.modules["bdsf"]
