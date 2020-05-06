# $Id$

# PyCommon is needed for OTB which is installed on the same server
lofar_package(SAS_OTDB 
  DEPENDS Deployment OTDB_Comps OTDB_SQL StaticMetaData WinCC_Datapoints PyCommon)
