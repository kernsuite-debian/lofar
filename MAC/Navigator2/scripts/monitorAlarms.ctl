//# monitorAlarms.ctl
//#
//#  Copyright (C) 2007-2008
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#uses "GCFCommon.ctl"
#uses "navFunct.ctl"



// This script needs to run the MainCU
// it monitors the state changes in the database, and will update the alarms accordingly
// 

bool bDebug=false;
bool occupied=false;

mapping mLastData;


void main()
{
  

  // Set the global statecolors/colornames.
  initLofarColors();
  
  // connect to debugflag to be able to switch debug on/off during run
  if (dpExists("scriptInfo.monitorAlarms.debug")) {
    dpConnect("debugCB",true,"scriptInfo.monitorAlarms.debug");
  } else {
    DebugTN("monitorAlarms.ctl:main|scriptInfo.monitorAlarms.debugpoint not found in Database");  
  } 

  // initialize the AlarmSystem
  Init();

}


private void debugCB(string dp1, bool debug)
{
  bDebug = debug;
}



void Init()
{
  string strSysName;
  
  strSysName = strrtrim( getSystemName(), ":" );
  
  string strQuery = "SELECT ALERT '_alert_hdl.._prior', '_alert_hdl.._ackable' " + 
                    "FROM '{LOFAR_ObsSW.status.childSumAlert,LOFAR_PermSW.status.childSumAlert,LOFAR_PIC.status.childSumAlert}' " +
                    "REMOTE ALL " +
                    "WHERE _SYS != \"" + strSysName + "\""; 
  
  dpQueryConnectSingle( "CallbackAlertLCU", true, "", strQuery );
}



void CallbackAlertLCU( string strIdent, dyn_dyn_anytype ddaAlerts )
{
  int x, y, iHighestPrio;
  bool bCame, bRetVal;
  string strHighestAlertClass;
  
  if (bDebug) LOG_DEBUG( "monitorAlarms.ctl:CallbackAlertLCU|=========================================================================================================================" );

  
  for( x=2; x<=dynlen(ddaAlerts); x++ )
  {
        
    if (bDebug) DebugN( " ---------------------------------------------------------------------------------------" );
    if (bDebug) DebugN( ddaAlerts[x] );

    // Declaration and initialization of variables
    dyn_string dsStationDPEs;
    string strStation, strStationDP, strStationDistChildSumAlertDPE;
    int iActState ;       
    dyn_int diPrios;

    
    // 12-jun-2017: to detect callbacks with the same data: first check the last known data in our mapping
    string strStationDPE = dpSubStr( ddaAlerts[x][1], DPSUB_SYS_DP_EL );
    if( mappingHasKey( mLastData, strStationDPE ) )
    {
      if( mLastData[strStationDPE] == ddaAlerts[x] )
      {
           if (bDebug) LOG_DEBUG( "monitorAlarms.ctl:CallbackAlertLCU|Data for " + strStationDPE+ " is not changed !!!" );
           continue;
      }
    }
    
    // Store data to detect next change
    mLastData[strStationDPE] = ddaAlerts[x];
    
    
    
    int iPrio        = ddaAlerts[x][3];
    bool bAckable    = ddaAlerts[x][4];

    // Get stationname and remove ':' on the end
    strStation = dpSubStr( ddaAlerts[x][1], DPSUB_SYS );
    strStation = strrtrim( strStation, ":" );
    
    // Determine station DP to use, based on DPE name: LOFAR_ObsSW, LOFAR_PermSW or LOFAR_PIC
    if( patternMatch( "*LOFAR_ObsSW*", ddaAlerts[x][1] ) )
    {
      dsStationDPEs = dpNames( "LOFAR_ObsSW*" + strStation, "Station"  );
    }
    else if( patternMatch( "*LOFAR_PermSW*", ddaAlerts[x][1] ) )
    {
      dsStationDPEs = dpNames( "LOFAR_PermSW*" + strStation, "Station"  );
    }
    else if( patternMatch( "*LOFAR_PIC*", ddaAlerts[x][1] ) )
    {
      dsStationDPEs = dpNames( "LOFAR_PIC_*" + strStation, "Station"  );
    }
    else
    {
      if (bDebug) DebugTN( __FUNCTION__ + "(): unrecognized alert '" + ddaAlerts[x][1] + "', skipp it !!" );
if (bDebug) LOG_DEBUG( "monitorAlarms.ctl:CallbackAlertLCU|unrecognized alert '" + ddaAlerts[x][1] + "', skipp it !!" );
      continue;
    }
    
    // Normally only one DPE should be found: take it
    if( dynlen(dsStationDPEs) >= 1 )
    {
      strStationDP = dpSubStr( dsStationDPEs[1], DPSUB_DP );
    }
    else
    {
      if (bDebug) LOG_DEBUG( "monitorAlarms.ctl:CallbackAlertLCU|strStationDP NOT FOUND FOR ALERT '" + ddaAlerts[x][1] + "' !!" );
      continue;
    }
    
    strStationDistChildSumAlertDPE = strStationDP + ".dist_childSumAlert";

    // Get actual state and list of summed-prios's (because they can't be get by the dpConnect)   
    dpGet( ddaAlerts[x][1] + ":_alert_hdl.._act_state",    iActState,
           ddaAlerts[x][1] + ":_alert_hdl.._summed_prios", diPrios );

    
    // First deactivate the alert to go to a 'default' state
    dpSet( strStationDistChildSumAlertDPE, 0 );
    dpDeactivateAlert( strStationDistChildSumAlertDPE, bRetVal, TRUE );

    // Now set the highest/actual prio of the sumalert as alert, this raises the alert
    dpActivateAlert( strStationDistChildSumAlertDPE, bRetVal, TRUE );        
    dpSet( strStationDistChildSumAlertDPE, iPrio );
   
    // If sum-alert is acked: ack our alert also
    if( iActState == DPATTR_ALERTSTATE_APP_ACK )
    {
      dpSet( strStationDistChildSumAlertDPE + ":_alert_hdl.._ack", DPATTR_ACKTYPE_SINGLE );
    }
    
    // If sum-alert is went-unacked: detect prio that cames below our prio and do dpSet, this causes the alert to go to the went-unacked state
    if( ( iActState == DPATTR_ALERTSTATE_APP_DISAPP_NOT_ACK ) ||
        ( iActState == DPATTR_ALERTSTATE_DISAPP_NOT_ACK ) )
    {
      int iNextPrio;
      
      dynSort( diPrios );
      
      for( y=1; y<=dynlen(diPrios); y++ )
      {
        // If this is prio is higher or equal then our current sumalert prio: stop
        if( diPrios[y] >= iPrio )
        {
          break;
        }
        
        // If this prio is higher then the previous one: takeover
        if( diPrios[y] > iNextPrio )
        {
          iNextPrio = diPrios[y];
        }
      }

      // dpSet determined prio
      dpSet( strStationDistChildSumAlertDPE, iNextPrio );

    }
   
     if (bDebug) LOG_DEBUG( "monitorAlarms.ctl:CallbackAlertLCU|Copied alert '" + ddaAlerts[x][1] + "' to strStationDistChildSumAlertDPE '" + strStationDistChildSumAlertDPE + "'" );
  }  
  
  
}

