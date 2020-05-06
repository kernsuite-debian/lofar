# $Id$

lofar_add_bin_scripts(MessageRouter)

set(MessageRouterConfs
  MessageRouter.conf.ccu001
  MessageRouter.conf.ccu199)

lofar_add_sysconf_files(${MessageRouterConfs})
