# $Id$

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/parset-additions.d/default/OutputProc.parset.in"
  "${CMAKE_CURRENT_BINARY_DIR}/parset-additions.d/default/OutputProc.parset"
  @ONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/parset-additions.d/default/FinalMetaDataGatherer.parset.in"
  "${CMAKE_CURRENT_BINARY_DIR}/parset-additions.d/default/FinalMetaDataGatherer.parset"
  @ONLY
)

# List of default/ config parsets:
# CMake cannot detect changes in this list, but for these files it doesn't need to.
file(GLOB _config_parsets_src RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}" "parset-additions.d/default/*.parset")
lofar_add_sysconf_files(${_config_parsets_src})

# cannot yet use lofar_add_sysconf_files since that wants to make a symlink to the source dir,
# but we've build them there directly.
file(GLOB _config_parsets_bin "${CMAKE_CURRENT_BINARY_DIR}/parset-additions.d/default/*.parset")   # configured .parset.in
install(FILES ${_config_parsets_bin} DESTINATION etc/parset-additions.d/default)
#lofar_add_sysconf_files(${_config_parsets_bin})

# To enable RSP raw data output, follow the instructions in the installed file below.
# NOTE: We do *not* create the override/ directory here, because the roll-out scripts symlink it: some project specific overrides must outlive roll-outs.
install(FILES "parset-additions.d/rspraw-enable.parset.OBSID" DESTINATION etc/parset-additions.d)

# Install script to generate StationStreams.parset for the live test system.
lofar_add_sbin_scripts(parset-additions.d/default/generateStationStreams.sh)
