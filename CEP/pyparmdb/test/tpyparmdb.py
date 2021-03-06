

from lofar.parmdb import *
import os
import sys


def createTestFile():
    """Create a test parmdb using parmdbm"""
    return os.system("""
parmdbm <<EOF > tpyparmdb_tmp.pdbout
 create tablename='tpyparmdb_tmp.pdb'
 add parm1 domain=[1,5,4,10],values=2
 add parm2 type='polc', domain=[1,5,4,10], values=[2,0.1], nx=2
 adddef parmdef values=[3,1], nx=2
 quit
EOF""")

### NOTE: parmdbm always returns exit code 0, so we cannot test if it worked
if createTestFile() != 0:
    raise RuntimeError("Could not create parmdb for tpyparmdb")

def showValues (pdb, pattern='*', nf=4, nt=2):
    # Get the names.
    print(pdb.getNames())
    # Get the range.
    rng = pdb.getRange()
    print(rng)
    # Get the values.
    print(pdb.getValuesStep(pattern, rng[0], rng[2], nf, rng[1], rng[3], nt, True))
    # Get values and grid.
    print(pdb.getValuesGrid(pattern, rng[0], rng[2], rng[1], rng[3]))
    # Print default names and values.
    print(pdb.getDefNames(pattern))
    print(pdb.getDefValues(pattern))

# The test is the same as in tParmFacade.cc.
# Open the parameterset (created in .run file).
pdb=parmdb("tpyparmdb_tmp.pdb")
print(">>>")
print(pdb.version("tree"))
print(pdb.version("full"))
print(pdb.version("top"))
print(pdb.version())
print("<<<")
showValues (pdb);
showValues (pdb, '', 1);
showValues (pdb, 'parm1', 1);
