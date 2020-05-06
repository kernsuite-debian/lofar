# $Id$

# PyCommon is needed for OTB, which uses dbcredentials. OTB is installed in parallel to this subsystem.
lofar_package(CCU_MAC 
  DEPENDS CEPCU CUDaemons CURTDBDaemons StaticMetaData MessageDaemons PyCommon)

