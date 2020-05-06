# $Id$

# Dragnet: LOFAR software install for the LOFAR DRAGNET cluster
# - ResourceTool + deps are needed for the resourcetool program to auto-update RADB periodically from DRAGNET nodes
lofar_package(Dragnet DEPENDS Online_Cobalt Offline ResourceTool XML_generator)

