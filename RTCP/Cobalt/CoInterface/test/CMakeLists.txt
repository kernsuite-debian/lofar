# $Id$

include(LofarCTest)

lofar_add_test(tBestEffortQueue tBestEffortQueue.cc)
lofar_add_test(tCorrelatedData tCorrelatedData.cc)
lofar_add_test(tLTAFeedback)
lofar_add_test(tMultiDimArray tMultiDimArray.cc)
lofar_add_test(tgcd_lcm tgcd_lcm.cc)
lofar_add_test(tpow2 tpow2.cc)
lofar_add_test(tSparseSet tSparseSet.cc)
lofar_add_test(tfpequals tfpequals.cc)
lofar_add_test(tcmpfloat DEPENDS cmpfloat)
lofar_add_test(tRSP tRSP.cc)


if(UNITTEST++_FOUND)
  lofar_add_test(t_cpu_utils t_cpu_utils.cc)
  lofar_add_test(tAlign tAlign.cc)
  lofar_add_test(tOMPThread tOMPThread.cc)
  lofar_add_test(tParset tParset.cc tParsetDefault.cc)
  lofar_add_test(tQueue2 tQueue2.cc)
  lofar_add_test(tRunningStatistics tRunningStatistics.cc)
  lofar_add_test(tTABTranspose tTABTranspose.cc tParsetDefault.cc)
  lofar_add_test(tRingCoordinates tRingCoordinates.cc)
  lofar_add_test(tRSPTimeStamp tRSPTimeStamp.cc)
  lofar_add_test(tSelfDestructTimer tSelfDestructTimer.cc)
endif(UNITTEST++_FOUND)
