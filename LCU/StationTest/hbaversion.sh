#!/bin/bash
#
# check the modem software version of the HBA-FE unit.
# modified for international and national
# version 10 HBA-FE is default on
# version 11 HBA-FE is default off (from PL610 2016 onwards)
# only check on element one in each tile
# 23-11-2018, M.J.Norden

let rspboards=`sed -n  's/^\s*RS\.N_RSPBOARDS\s*=\s*\([0-9][0-9]*\).*$/\1/p' /opt/lofar/etc/RemoteStation.conf`
let nrcus=8*$rspboards

version=11


if [ $nrcus -eq 96 ] ; then
   echo "HBA-FE modem version V-$version check national station"  
   sleep 2
   python3 verify.py --brd rsp0,rsp1,rsp2,rsp3,rsp4,rsp5,rsp6,rsp7,rsp8,rsp9,rsp10,rsp11 --fpga blp0,blp1,blp2,blp3 --te tc/hba_server.py --server 1 --server_access uc --server_reg version --server_func gb --data $version 
else
   echo "HBA-FE modem version V-$version check international station"  
   sleep 2
   python3 verify.py --brd rsp0,rsp1,rsp2,rsp3,rsp4,rsp5,rsp6,rsp7,rsp8,rsp9,rsp10,rsp11,rsp12,rsp13,rsp14,rsp15,rsp16,rsp17,rsp18,rsp19,rsp20,rsp21,rsp22,rsp23 --fpga blp0,blp1,blp2,blp3 --te tc/hba_server.py --server 1 --server_access uc --server_reg version --server_func gb --data $version
fi


