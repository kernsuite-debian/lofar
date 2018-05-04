# $Id$

lofar_package(StaticMetaData 1.0)

lofar_add_sbin_scripts(createFiles)

# These files end up in ${prefix}/etc
file(GLOB sysconf_data RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}" *.conf)
lofar_add_sysconf_files(
  ${sysconf_data}
  StationInfo.dat
  ControlInfo.dat)

# These files end up in ${prefix}/etc/StaticMetaData
# lofar_add_sysconf_files can only install in the same
# relative dir as in the source, hence we've put a symlink
# StaticMetaData -> . in this directory.
file(GLOB staticmeta_data RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}"
  *.tmpl 
  *.test 
  *.dat 
  AntennaArrays/*.conf*
  AntennaPos/*.conf*
  CableDelays/*.conf*
  iHBADeltas/*.conf*
  AntennaFields/*.conf*
  Attenuation/*.conf*)
lofar_add_sysconf_files(${staticmeta_data} DESTINATION StaticMetaData)
