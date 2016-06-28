# $Id: CMakeLists.txt 15040 2010-02-22 16:44:49Z diepen $

include(LofarPackageVersion)

lofar_add_library(spwcombine
  Package__Version.cc)

lofar_add_bin_program(combinespw 
  SPWCombine.cc
  Combiner.cc
  CombinerProcessControl.cc)

lofar_add_bin_program(versionspw_combine versionspw_combine.cc)
