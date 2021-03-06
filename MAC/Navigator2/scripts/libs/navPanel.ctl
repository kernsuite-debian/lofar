// navPanel.ctl
//
//  Copyright (C) 2002-2004
//  ASTRON (Netherlands Foundation for Research in Astronomy)
//  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation; either version 2 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  $Id$
//
///////////////////////////////////////////////////////////////////
// Ctrl scripts that are generic for all panels
///////////////////////////////////////////////////////////////////
//
// Functions and procedures
//
// navPanel_initPanel                : sets up initial stuff for each panel
// navPanel_setEvent                 : fires an event from a Panel
// navPanel_showVersion              : shows version info in txt_version object
// navPanel_showTemp                 : shows temperature in txt_temperature object
// navPanel_checkDataPath            : check the dataflow to set dataFlowElement in the RCU panels on/off 
// navPanel_showLogging              : show logMsg and historical data if any
// navPanel_updateLogging            : callback for showLogging
// navPanel_addLogMsg                : adds a new log Msg to the logTable


#uses "navigator.ctl"

global string 		itsEventDp         = "";
global string     itsActionDp        = "";
global dyn_string itsSelectionDp     = "";
global string     itsNavigatorObject = "";
global string     sysName            = "";

global string     g_craftPath        = "http://craft.astron.nl/";

// Define pathchoices to be able to check datapaths in RCU screen
global bool InputEnable=FALSE;
global bool LBLEnable=FALSE;
global bool LBHEnable=FALSE;
global bool HBAEnable=FALSE;
global bool bandSelLblLbh=FALSE;
global bool VlEnable=FALSE;
global bool VhEnable=FALSE;
global bool bandSelLbaHba=FALSE;
global bool VddVccEnable=FALSE;

bool undocked = false;


// ****************************************
// Name : navPanel_initPanel
// ****************************************
// Description:  
//   Set up the common panel stuff
//
// Params:
//   objectName    :  The navigator object where this panel belongs to. (eg. fw_viewBox)
//
// ***************************************
void navPanel_initPanel(string objectName) {
  
  // sets global to busy
  g_objectReady=false;
  
  undocked = false;
  
  //check if the panle is in the framework or started via the undock button.
  if (isDollarDefined("$undocked") ){
    undocked = $undocked;
  }
  
  itsNavigatorObject = objectName;
  itsActionDp    = DPNAME_NAVIGATOR + g_navigatorID + "." + objectName + ".action";  
  itsEventDp     = DPNAME_NAVIGATOR + g_navigatorID + "." + objectName + ".event";
  itsSelectionDp = DPNAME_NAVIGATOR + g_navigatorID + "." + objectName + ".selection";
  sysName = dpSubStr(g_currentDatapoint,DPSUB_SYS);
  
  navFunct_clearGlobalLists();
  
  // empty the hardwareList
  if (dpExists(DPNAME_NAVIGATOR + g_navigatorID + ".hardwareList")) {
    dpSet(DPNAME_NAVIGATOR + g_navigatorID + ".hardwareList",makeDynString(""));
  }
  
  // empty the observationsList
  if (dpExists(DPNAME_NAVIGATOR + g_navigatorID + ".observationsList")) {
    dpSet(DPNAME_NAVIGATOR + g_navigatorID + ".observationsList",makeDynString(""));
  }
  
  // empty the processesList
  if (dpExists(DPNAME_NAVIGATOR + g_navigatorID + ".processesList")) {
    dpSet(DPNAME_NAVIGATOR + g_navigatorID + ".processesList",makeDynString(""));
  }
  
  if ( dpExists(itsActionDp) ) {
    VIEWBOXACTIONDP=itsActionDp;
    if (dpConnect("doAction",false,itsActionDp) == -1){
      LOG_ERROR("navPanel.ctl:navPanel_initPanel|Couldn't connect to "+itsActionDp+ " " + getLastError());
    }        
  } else {
    LOG_ERROR("navPanel.ctl:navPanel_initPanel|"+itsActionDp+ " does not exist");
  }      
}

// ****************************************
// Name : navPanel_setEvent
// ****************************************
// Description:  
//   Set the selection and eventpoint on a selected sender object
//
// Params:
//   aSelection  :  The selection that might be of importance for the event handling
//   anEvent     :  The event we want to be triggered
//
// ***************************************
void navPanel_setEvent(dyn_string aSelection,string anEvent) {
  if (navigator_initializing()) {
    return;
  }
  string event=itsNavigatorObject+"|"+anEvent;
  if (dpExists(itsEventDp) && dpExists(itsSelectionDp)) {
     dpSet(itsEventDp,event,itsSelectionDp,aSelection);
  } else {
    LOG_ERROR("navPanel.ctl:navPanel_setEvent| "+itsEventDp +" or " +itsSelectionDp + " Does not exist yet");     
  }
} 

// ****************************************
// Name: navPanel_showVersion   
// ****************************************
//   Displays the version of the object in txt_version
//
// ****************************************
navPanel_showVersion(string dp1, string version)
{
    if (version !="")
    {
      setValue("txt_version", "text", "ver: " +version);
    }
    else
    {
      setValue("txt_version", "text", "ver: x.x");
    }
} 

// ****************************************
// Name: navPanel_showTemp   
// ****************************************
//   Displays the temperature of the object in txt_temperature
//
// ****************************************
navPanel_showTemp(string dp1, float temp)
{
    if (temp !="")
    {
      setValue("txt_temperature", "text", +temp);
      setValue("txt_temperature", "visible", TRUE);      
    }
    else
    {
      setValue("txt_temperature", "text", "xxxx");
      setValue("txt_temperature", "visible", FALSE);
    }
}

// ****************************************
// Name: navPanel_checkDataPath   
// ****************************************
//    Check the dataflow to set dataFlowElement in the RCU panels on/off 
//           
// ****************************************
navPanel_checkDataPath() {

  bool lbaPath = TRUE;
  bool hbaPath = TRUE;
  bool path    = TRUE;


  // check on LBL/LBH/HBA Enable level
  if (!LBLEnable && !LBHEnable) {
    lbaPath = FALSE;
  }

  if (!HBAEnable) {
    hbaPath = FALSE;
  }


  // check on bandSelLblLbh level
  if(lbaPath) {
    if ((bandSelLblLbh && !LBHEnable) ||
         (!bandSelLblLbh && !LBLEnable))  {
      lbaPath = FALSE;
    }
  }

  // Check on VlEnable and VhEnable Level
  if (lbaPath) {
    lbaPath = VlEnable;
  }
  if (hbaPath) {
    hbaPath = VhEnable;
  }

  // set lba/hba line colors
  if (lbaPath) {
    setValue("line1_lba","foreCol","Lofar_operational");
    setValue("line2_lba","foreCol","Lofar_operational");
  } else {
    setValue("line1_lba","foreCol","Lofar_off");
    setValue("line2_lba","foreCol","Lofar_off");
  }

  if (hbaPath) {
    setValue("line1_hba","foreCol","Lofar_operational");
    setValue("line2_hba","foreCol","Lofar_operational");
  } else {
    setValue("line1_hba","foreCol","Lofar_off");
    setValue("line2_hba","foreCol","Lofar_off");
  }
  

  // determine remainder path based on the above


  if (!lbaPath && !hbaPath) {
    path = FALSE;
  }

  // check based on bandSelLbaHba
  if (path) {
    if ((bandSelLbaHba && hbaPath) ||
        (bandSelLbaHba && !lbaPath) ){
      path = FALSE;
    }
  }

  if (path) {
    setValue("line1_path","foreCol","Lofar_operational");
  } else {
    setValue("line1_path","foreCol","Lofar_off");
  }

  // check based on VddVccEnable
  if (path) {
    path = VddVccEnable;
  }
 
  if (path) {
    setValue("line2_path","foreCol","Lofar_operational");
  } else {
    setValue("line2_path","foreCol","Lofar_off");
  }

  // check based on InputEnable
  if (path) {
    path = InputEnable;
  }

  if (path) {
    setValue("line3_path","foreCol","Lofar_operational");
  } else {
    setValue("line3_path","foreCol","Lofar_off");
  }
}

// ****************************************
// Name: navPanel_showLogging   
// ****************************************
//    Connects to the given datapoint .logMsg and it's historical data (if any)
//    and logs all into the logWindow
//           
// ****************************************
navPanel_showLogging(string aDP)
{
  LOG_TRACE("navPanel.ctl:navPanel_showLogging| Datapoint: ",aDP);
	
  string dpLog = aDP+".process.logMsg";
  string systemName = dpSubStr(dpLog,DPSUB_SYS);
  string bareDP     = dpSubStr(dpLog,DPSUB_DP_EL_CONF_DET_ATT);

  myLogTable.deleteAllLines();
 
  if(dpExists(dpLog)) {
    // initialize the logging table with historical data:
    dyn_dyn_anytype tab;
    int z;
    time tStart;
    time tStop;
    tStop = getCurrentTime();
    tStart = tStop - 3*3600; // three hours of history
	
    string query="";
            
    if (systemName != MainDBName) {     
      query = "SELECT ALL '_original.._value' FROM '" + dpLog + "' REMOTE'"+systemName +"' TIMERANGE(\"" +
              formatTime("%Y.%m.%d %H:%M:%S",tStart) + "\",\"" +
              formatTime("%Y.%m.%d %H:%M:%S",tStop) + "\",1,0) LAST 100";
    } else {
      query = "SELECT ALL '_original.._value' FROM '" + dpLog + "' TIMERANGE(\"" +
              formatTime("%Y.%m.%d %H:%M:%S",tStart) + "\",\"" +
              formatTime("%Y.%m.%d %H:%M:%S",tStop) + "\",1,0) LAST 100";
    }
      
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|Query: " + query);
    dpQuery(query, tab);
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|Found: " + tab + " length: " + dynlen(tab));
	 	 
	 	
    for(z=2;z<dynlen(tab);z++) {
      navPanel_addLogMessage(tab[z][2]);
    }
	
    // connect to logging
    if (dpConnect("navPanel_updateLogging",dpLog) == -1) {
      LOG_ERROR("navPanel.ctl:navPanel_showLogging|Couldn't connect to "+dpLog+ " " + getLastError());
    }
  } else {
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|error connecting to: "+ dpLog);
  }    
}

// ****************************************
// Name: navPanel_updateLogging   
// ****************************************
//    callback for navPanel_showLogging
//           
// ****************************************
navPanel_updateLogging(string dpe, string logMsg)
{
  LOG_TRACE("navPanel.ctl:navPanel_showLogging|LogMsg: "+logMsg);
  if (logMsg != "") {
    navPanel_addLogMessage(logMsg);
  }
}

// ****************************************
// Name: navPanel_addLogMsg   
// ****************************************
//    places a log Msg in the appropiate table
//    split lines like:
//    13-11-06 10:06:00.519|INFO|MAC.GCF.PAL.SAL|Set value of property 'MCU001:LOFAR_PermSW_MACScheduler.OTDB.lastPoll'|GSA_Service.cc:661
//    into relevant pieces
//           
// ****************************************
navPanel_addLogMessage(string aMsg)
{


  LOG_TRACE("navPanel.ctl:navPanel_addLogMsg|msg: " + aMsg);
  if (aMsg != "") {


    dyn_string msgParts;
    string dateTime="";
    string level="";
    string source="";
    string logMsg="";
    string codeLine="";
    bool error=false;

    
    // we need to cut out all \r and \n from the string
    strreplace(aMsg,"\r","");
    strreplace(aMsg,"\n","");
    
    msgParts = strsplit(aMsg,"|");
    
    if (dynlen(msgParts) >=1) {
      dateTime = msgParts[1];
    } else {
      error=true;
    }
    if (dynlen(msgParts) >=2) {
      level    = msgParts[2];
    } else {
      error=true;
    }
    if (dynlen(msgParts) >=3) {
      source   = msgParts[3];
    } else {
      error=true;
    }

    if (dynlen(msgParts) >=4) {
      logMsg = msgParts[4];
    } else {
      error=true;
    }

    if (dynlen(msgParts) >=5) {
      codeLine = msgParts[5];
    } else {
      error=true;
    }
    
    dyn_string d1=navFunct_getLogColor(level,level );
	
	
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|dateTime: " + dateTime);
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|level: " + level);
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|source: " + source);
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|logMsg: " + logMsg);
    LOG_DEBUG("navPanel.ctl:navPanel_showLogging|codeLine: " + codeLine);

    if (!error) {
      myLogTable.appendLine("time",dateTime,"level",d1,"source",source,"message",navFunct_getLogColor(logMsg,level),"code",codeLine);
      myLogTable.lineVisible(-1);
    }
  }
}

// ****************************************
// Name: navPanel_statePopup   
// ****************************************
//    creates a popup where the user can (recursively)
//    set the states of objects.
//           
// ****************************************
void navPanel_statePopup(string baseDP) {
  dyn_string popup;

  // NCFObjectState vars
  int state;
  
  // define the popupMenu
  LOG_DEBUG("navPanel.ctl:navPanel_statePopup|define popup for DP: "+baseDP);
 
  dynAppend(popup,"PUSH_BUTTON,Set State,1,1");
  
  LOG_DEBUG("navPanel.ctl:navPanel_statePopup|popup composed");
  if (popupMenu(popup,state)<0 || !state>0) {
    return;
  }
  
  LOG_DEBUG("navPanel.ctl:navPanel_statePopup|popup returned: "+state);
  
  if( state == 1 )
  {
    LOG_DEBUG("navPanel.ctl:navPanel_statePopup|Open popup 'Popups/Popup_SetState.pnl' for baseDP '" + baseDP + "'");
    ChildPanelOnRelativModal( "Popups/Popup_SetState.pnl", 
                              "SetState_" + baseDP,
                              makeDynString( "$baseDP:" + baseDP ),
                              10, 10 );
  }
}

