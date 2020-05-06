# $Id$

# Detect list of kernel sources to install.
# CMake cannot detect changes in this list, but for kernel sources it doesn't need to.
file(GLOB _kernel_sources RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}" "gpu/kernels/*.cu" "gpu/kernels/*.cuh" "gpu/kernels/*.cl")
lofar_add_data_files(${_kernel_sources})
