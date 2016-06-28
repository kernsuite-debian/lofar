# $Id: CMakeLists.txt 32581 2015-10-15 13:45:24Z loose $

include(PythonInstall)

# Python modules.
python_install(
  __init__.py 
  solfetch.py
  solplot.py
  solflag.py
  DESTINATION lofar/solutions)

python_install(
  #__init__.py
  solverquery.py
  plotwindow.py
  plothistogram.py
  plotcorrmatrix.py
  DESTINATION lofar/bbs)

lofar_add_bin_scripts(
  addImagingColumns.py
  parmdbplot.py
  casapy2bbs.py
  solverdialog.py)
