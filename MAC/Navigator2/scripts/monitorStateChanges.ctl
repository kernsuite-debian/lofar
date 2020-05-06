//# monitorStateChanges.ctl
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
//#  $Id: monitorStateChanges.ctl,v 1.4 2007/06/26 08:59:29 coolen Exp $
#uses "GCFCommon.ctl"
#uses "navFunct.ctl"


// This script needs to run on every CSU, CCU and MainCU
// it monitors the point where the state changes are being send to and updates the point in the database accordingly.
// it will also set comments into the alarmsystem accordingly.
// in the past it also tried to update all childStates, but this will be done by the childSumAlert automaticly from now on
// 

global bool isConnected=false;
global bool bDebug = false;

main () {
  
  // check if we run on a standAlone system
  if (!isDistributed() ) {
    MainDBName         = getSystemName();
    MainDBID           = getSystemId();
    DebugN("Running in standAlone modus");
  }  

  // Set the global statecolors/colornames.
  initLofarColors();
  
  // connect to debugflag to be able to switch debug on/off during run
  if (dpExists("scriptInfo.transferMPs.debug")) {
    dpConnect("debugCB",true,"scriptInfo.monitorStateChanges.debug");
  } else {
    DebugTN("monitorStateChanges.ctl:main|scriptInfo.monitorStateChanges.debugpoint not found in dbase");  
  } 


  // subscribe to the statechange update mechanism
  subscribeObjectStateChange();
  subscribeObjectStateChanges();
}

private void debugCB(string dp1, bool debug) {
  if (bDebug != debug) bDebug=debug;
}

///////////////////////////////////////////////////////////////////////////
//Function subscribeObjectStateChange
// 
// subscribes to the __navObjectState DP of the database to monitor 
// possible stateChanges,
//
///////////////////////////////////////////////////////////////////////////
void subscribeObjectStateChange() {

  if (bDebug){
     DebugN("monitorStateChanges.ctl:subscribeObjectStateChange|entered");
   }
  // Routine to connnect to the __navObjectState point to trigger statechanges

  dpConnect("objectStateTriggered",false,"__navObjectState.DPName",
            "__navObjectState.stateNr",
            "__navObjectState.message",
            "__navObjectState.force");
  
}

///////////////////////////////////////////////////////////////////////////
//Function subscribeObjectStateChanges
// 
// subscribes to the __navObjectState DP of the database to monitor 
// possible stateChanges,
//
///////////////////////////////////////////////////////////////////////////
void subscribeObjectStateChanges() {

  if (bDebug){
     DebugN("monitorStateChanges.ctl:subscribeObjectStateChanges|entered");
   }
  // Routine to connnect to the __navObjectStates point to trigger statechanges

  dpConnect("objectStatesTriggered",false,"__navObjectStates.DPNames",
            "__navObjectStates.stateNrs",
            "__navObjectStates.messages",
            "__navObjectStates.force");
  
}
 

///////////////////////////////////////////////////////////////////////////
//Function objectStateTriggered
// 
// Callback where a trigger of __navObjectState is handled.
//
// Added 26-3-2007 A.Coolen
///////////////////////////////////////////////////////////////////////////
void objectStateTriggered(string dp1, string trigger,
                          string dp2, int state,
                          string dp3, string message,
                          string dp4, bool force) {

  if (trigger == "") return;

  // To keep it simple entering here we just will put the points into dynamic vars and call the objectStatesTriggered
  // variant
  dyn_string dps = makeDynString(trigger);
  dyn_int states = makeDynInt(state);
  dyn_string messages = makeDynString(message);
  dyn_bool forces = makeDynBool(force);
  
  dpSet("__navObjectStates.DPNames",dps,
        "__navObjectStates.stateNrs",states,
        "__navObjectStates.messages",messages,
        "__navObjectStates.force",forces);
}

void objectStatesTriggered(string dp1, dyn_string triggers,
                           string dp2, dyn_int states,
                           string dp3, dyn_string messages,
                           string dp4, dyn_bool forces) {

  // __navObjectStates change.
  // This point should have points like:
  //
  // LOFAR_PIC_Cabinet0_Subrack0_RSPBoard0_RCU0.status.state
  // 1 (= good)
  // a msg indicating extra comments on the state
  // true/false
  //
  //                               
  // This State should be set to childState=bad in all upper (LOFAR-PIC_Cabinet0_Subrack0_RSPBoard0) treenodes
  // ofcourse we need to monitor if this statechange is allowed.
  // if force false we also monitor the first digit of the state (1-5) if the 1st digit of the current state matches, no
  // state change allowed (to avoid ACK'ed alarms go back to came for example)
  //                               
  // The force bool will be used to monitor if lowering a state >= 10 is allowed.
  // false means NO, true means force a change.
  
  if (dynlen(triggers) < 1 || triggers[1] == "") return;

  if (bDebug) DebugTN("monitorStateChanges.ctl:objectStatesTriggered|entered with triggers:", triggers);
  
  dyn_string datapoints;
    
  for ( int i = 1; i <= dynlen(triggers); i++) {
    string element   = "";
  
    // the datapointname can hold _ and . seperated path elements.  however, after the last point there should be
    // status.state
    //
    // strip the system name
    string dp = dpSubStr(triggers[i],    DPSUB_DP_EL);
    
    if (strlen(dp) > 0) {

      int start=strpos(dp,".status.state");
      if (start < 0 || strlen(dp) > (start + strlen(".status.state"))) {
        DebugTN("monitorStateChanges.ctl:objectStatesTriggered|ERROR: No status.state found in DPName, or not last element in name: " + dp);
        return;
      }
    
      // strip the last status.state from the datapoint name.
      // the remainder is used as path
      string bareDP = substr(dp,0,start);

      // if all needed values are available we can start doing the major update.
      if (states[i] >= 0 && bareDP != "" && dpExists(bareDP + ".status.state")){
        dynAppend(datapoints, bareDP);
      } else {
        DebugTN("monitorStateChanges.ctl:objectStatesTriggered|result: Wrong datapoint or state. DP: " + datapoint +"."+element+ " State: "+state );
      }
    }
  }
  setStates(datapoints,states,messages,forces);
}


///////////////////////////////////////////////////////////////////////////
//Function setStates
// 
// Does the setting of the involved states.
//
// datapoints     = the base datapoints that need to be set
// states         = new states
// messages       = messages if supplied
// force          = boolean indicating if states >= 10 are allowed to be lowered or not and check first digit old against new state
//
// Added 3-4-2007 A.Coolen
///////////////////////////////////////////////////////////////////////////
void setStates(dyn_string datapoints,dyn_int states,dyn_string messages,dyn_bool force) {

  if (bDebug) DebugN("monitorStateChanges.ctl:setStates|entered");

  string dp;
  for (int i = 1; i <= dynlen(datapoints); i++) 
  {
    // set the state value of the dp's
    
    int aVal;
    string aMsg;
    dpGet(datapoints[i]+".status.state",aVal,datapoints[i]+".status.message",aMsg);
 
  // We used to have our own alarmsystem with a simulated WENT and CAME.
  // They were set as 43 and 46 for suspicious and 53 and 56 for broken.
  // as there are still c++ controllers using that system we will check for them here and change
  // them to their corresponding alarm numer (40 and 50)
  // this should be altered in the c++ controllers eventually obviously....
  
    if (states[i] == 43 || states[i] == 46) {
      states[i] = 40;
    } else if (states[i] == 53 || states[i] == 56) {
      states[i] = 50;
    }
    
    if (states[i] > -1 && (states[i] != aVal || messages[i] != aMsg)) {
      if (force[i]) {
        dpSet(datapoints[i]+".status.state",states[i]);
      } else {
        if (bDebug) DebugN("monitorStateChanges.ctl:setStates|original val: "+aVal+ " state to set to: " + states[i]);
        if (aVal <=10 && states[i] == 0) {
          dpSet(datapoints[i]+".status.state",states[i]);
        } else if (aVal <= states[i] && floor(aVal/10)!=floor(states[i]/10) ){
          dpSet(datapoints[i]+".status.state",states[i]);
        } else {
          if (bDebug) DebugN("monitorStateChanges.ctl:setStates|State not changed because of force conditions");
          return;
        }
      }
      dpSet(datapoints[i]+".status.message",messages[i]);
      
      // Call function to add message to alertcomment (call as thread to avoid eventload during callback
      startThread( "SetAlertComment", datapoints[i]+".status.state", messages[i] );
       
    } else {
      if (bDebug) DebugN("monitorStateChanges.ctl:setStates|Equal value or state < 0, no need to set new state");
    }   
  }
}




// This function is started as thread to avoide datapoint handling in a callback, we
void SetAlertComment( string dpe, string msg, int delaymsec = 10 )
{
  string strQuery;
  string strAlertComment;
  dyn_dyn_anytype ddaAlerts;
  atime atLastAlert;
  
  delay(0,delaymsec);
  
  // convert to Alertsystem msg format
  string message = getUserName() + "|" + (string)getCurrentTime() + "|" + msg;
  
  // Get alerts of given dpe
  strQuery = "SELECT ALERT '_alert_hdl.._prior' FROM '" + dpSubStr( dpe, DPSUB_DP_EL ) + "'";
  dpQuery( strQuery, ddaAlerts );
  
  if( dynlen(ddaAlerts) < 2 )
    return;
  
  // Remove header
  dynRemove( ddaAlerts, 1 );
  
  // Sort alerts on time, descending to get the latest one
  dynDynSort( ddaAlerts, 2,false );

  if (bDebug) DebugN( "monitorStateChanges.ctl:SetAlertComment|entered with datapoint-element: "+ dpe +" message: "+message+" delaymsec: "+delaymsec);
  
  // Takeover latest alert time
  atLastAlert = ddaAlerts[1][2];
  
  // First get current alarm comment
  alertGet( (time)atLastAlert, getACount(atLastAlert), dpSubStr( getAIdentifier(atLastAlert), DPSUB_SYS_DP_EL_CONF_DET ) + "._comment", strAlertComment );
  
  // Add given comment
  strAlertComment += message + "\uA7";
  
  // Store new comment
//  alertSet( (time)atLastAlert, getACount(atLastAlert), dpSubStr( getAIdentifier(atLastAlert), DPSUB_SYS_DP_EL_CONF_DET ) + "._comment", strAlertComment );   
  alertSet( (time)atLastAlert, getACount(atLastAlert), dpSubStr( getAIdentifier(atLastAlert), DPSUB_SYS_DP_EL_CONF_DET ) + "._comment",     strAlertComment,
            (time)atLastAlert, getACount(atLastAlert), dpSubStr( getAIdentifier(atLastAlert), DPSUB_SYS_DP_EL_CONF_DET ) + "._add_value_5", msg );   

}
