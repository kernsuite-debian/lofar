# $Id$

lofar_add_bin_program(ApplController 
  ApplControllerMain.cc
  ACCmdImpl.cc
  ACDaemonComm.cc
  APAdmin.cc
  APAdminPool.cc
  CmdStack.cc
  forkexec.cc
  ItemList.cc
  ProcRule.cc
  ProcRuler.cc
  PR_Shell.cc
  PR_MPI.cc
  PR_BGL.cc
  StateEngine.cc
  ApplController.cc)
                                                  
lofar_add_bin_program(ACDaemon 
  ACDaemonMain.cc
  ACRequestPool.cc
  ACDaemon.cc
  forkexec.cc)

lofar_add_bin_program(ACcli ACcli.cc)

lofar_add_bin_program(ACuserMenu ACuserMenu.cc)

lofar_add_bin_scripts(
  startAP.sh
  startMPI.sh
  stopAP.sh
  stopMPI.sh)
  
install(FILES
  ACDaemon.log_prop 
  ACDaemon.conf
  ApplController.log_prop
  ACuserMenu.log_prop
  DESTINATION etc)
