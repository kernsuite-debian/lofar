# $Id$

include(LofarPackageVersion)

# Create symbolic link to include directory.
execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink 
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_BINARY_DIR}/include/${PACKAGE_NAME})

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/cuda_config.h.in"
  "${CMAKE_BINARY_DIR}/include/cuda_config.h"  # internal, no need to install
)

set(_gpuproc_sources
  #Package__Version.cc
  BandPass.cc
  CommandThread.cc
  FilterBank.cc
  Flagger.cc
  global_defines.cc
  MPIReceiver.cc
  Package__Version.cc
  SysInfoLogger.cc
  Station/StationNodeAllocation.cc
  Station/StationInput.cc
  Station/StationTranspose.cc
  Station/RSPRawSender.cc
  Storage/StorageProcess.cc
  Storage/StorageProcesses.cc
)

list(APPEND _gpuproc_sources
  gpu_wrapper.cc
  gpu_utils.cc
  KernelFactory.cc
  PerformanceCounter.cc
  Kernels/Kernel.cc
  Kernels/BeamFormerKernel.cc
  Kernels/BeamFormerTransposeKernel.cc
  Kernels/CoherentStokesTransposeKernel.cc
  Kernels/CoherentStokesKernel.cc
  Kernels/CorrelatorKernel.cc
  #Kernels/DedispersionBackwardFFTkernel.cc
  #Kernels/DedispersionChirpKernel.cc
  #Kernels/DedispersionForwardFFTkernel.cc
  Kernels/DelayAndBandPassKernel.cc
  Kernels/BandPassCorrectionKernel.cc
  Kernels/FFT_Kernel.cc
  Kernels/FFT_Plan.cc
  Kernels/FIR_FilterKernel.cc
  Kernels/IncoherentStokesKernel.cc
  Kernels/IncoherentStokesTransposeKernel.cc
  Kernels/IntToFloatKernel.cc
  Kernels/FFTShiftKernel.cc
  Kernels/ZeroingKernel.cc
  #Kernels/UHEP_BeamFormerKernel.cc
  #Kernels/UHEP_InvFFT_Kernel.cc
  #Kernels/UHEP_InvFIR_Kernel.cc
  #Kernels/UHEP_TransposeKernel.cc
  #Kernels/UHEP_TriggerKernel.cc
  Pipelines/Pipeline.cc
#    Pipelines/UHEP_Pipeline.cc
  SubbandProcs/SubbandProc.cc
  SubbandProcs/SubbandProcInputData.cc
  SubbandProcs/SubbandProcOutputData.cc
  SubbandProcs/KernelFactories.cc
  SubbandProcs/CorrelatorStep.cc
  SubbandProcs/BeamFormerPreprocessingStep.cc
  SubbandProcs/BeamFormerCoherentStep.cc
  SubbandProcs/BeamFormerIncoherentStep.cc

#    SubbandProcs/UHEP_SubbandProc.cc
)

lofar_add_library(gpuproc ${_gpuproc_sources})
if(CUDA_cufft_LIBRARY)
  target_link_libraries(gpuproc ${CUDA_cufft_LIBRARY})
endif()

lofar_add_bin_program(rtcp rtcp.cc)

lofar_add_bin_program(station_stream Station/station_stream.cc)
lofar_add_bin_program(gpu_load gpu_load.cc)

# install scripts used to run an observation under bin
lofar_add_bin_scripts(
  scripts/cobalt_functions.sh
  scripts/CobaltControl.sh
  scripts/generate_globalfs_locations.py
  scripts/runObservation.sh
  scripts/startstopkeys.sh
  scripts/startBGL.sh
  scripts/stopBGL.sh
  scripts/watchlogs.sh)

# install support scripts (install, roll-out, debugging) into sbin
lofar_add_sbin_scripts(
  scripts/bw_monitor.sh
  scripts/cobaltswitch
  scripts/Cobalt_install.sh
  scripts/CobaltVersions.sh
  scripts/setloglevels.sh)

# install logprop files
lofar_add_sysconf_files(
  rtcp.log_prop
  Station/station_stream.log_prop
  scripts/watchlogs-multitail.conf
  DESTINATION .)
