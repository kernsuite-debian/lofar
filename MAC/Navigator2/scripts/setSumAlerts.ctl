#uses "GCFCommon.ctl"



bool bDebug;

void main()
{
  
  
  // connect to debugflag to be able to switch debug on/off during run
  if (dpExists("scriptInfo.setSumAlerts.debug")) {
    dpConnect("debugCB",true,"scriptInfo.setSumAlerts.debug");
  } else {
    DebugTN("setSumAlerts.ctl:main|scriptInfo.setSumAlerts.debugpoint not found in Database");  
  } 

  delay(0,100);
  
  if (dpExists("scriptInfo.setSumAlerts.runDone")) {
    dpConnect("setSumAlerts",true,"scriptInfo.setSumAlerts.runDone");
  } else {
    DebugTN("setSumAlerts.ctl:main|scriptInfo.setSumAlerts.runDone point not found in Database");  
  } 


}


private void debugCB(string dp1, bool debug)
{
  bDebug = debug;
}


private void setSumAlerts( string strDPE, bool bRunDone )
{
  int x, y;
  string strDPE, strParentDP;
  dyn_string dsParentDPEs, dsChilds, dsChildDPEs, dsParentRelations;

  // If we're already done: do nothing  
  if( bRunDone )
    return;
  
  DebugTN("setSumAlerts.ctl:main|start set of sumAlerts");     
    
  // Get all DPE's with a 'childSumAlert'
  dsParentDPEs = dpNames( "*.**.childSumAlert" );

  dynSort(dsParentDPEs);
  
  // Go through sumalerts
  for( x=1; x<=dynlen(dsParentDPEs); x++ )
  {
    bool bRetVal1, bRetVal2, bLeaf;
    int iRetVal, iAlertHdlType;
    string strDPE;
    dyn_string dsChilds, dsChildDPEs;
    
    strParentDP = dpSubStr( dsParentDPEs[x], DPSUB_DP );
    
    // Use DPE part, and remove last parts (normally '.state.childSumAlert')
    strDPE = dpSubStr( dsParentDPEs[x], DPSUB_DP_EL );
    strDPE = RemoveLastDpeParts(strDPE);
    
    // Skip master datapoints and leaf=True points
    if( patternMatch( "*_mp*", strDPE ))
    {
      continue;
    }
      
    if( strDPE == "" )
    {
      continue;
    }

    dpGet(strDPE+".status.leaf",bLeaf);
    if (bLeaf)
    {
      continue;
    }
    

    if (bDebug) 
    {
      DebugTN("Working on: " + strDPE);
    }

    // Get childs of this DPE
    dsChilds = GetChilds( strDPE );
    
    // Get objects with a relation to this parent
    if( dpTypeName( strParentDP ) == "RCU" )
    {
      dsParentRelations = GetRelationsToParent( strParentDP );
      dynAppend( dsChilds, dsParentRelations );
    }
    
    // For each child: get DPE's to add to sumalerts and append to list
    for( y=1; y<=dynlen(dsChilds); y++ )
    {
      dynAppend( dsChildDPEs, GetChildDPEs( dsChilds[y] ) );
    }

    
    // Check if this DPE has an alert_hdl of type sumalert
    dpGet( dsParentDPEs[x] + ":_alert_hdl.._type", iAlertHdlType );
    
    if( iAlertHdlType == DPCONFIG_SUM_ALERT)
    {
      // If list is empty: use dummybit
      if( dynlen(dsChildDPEs) <= 0 )
      {
        DebugTN( "setSumAlerts(): empty dsChildDPEs list for DPE '" + dsParentDPEs[x] + "', 'DummyBit' will be used !!" );
        dsChildDPEs = makeDynString( "DummyBit." );
      }

      // First deactivate the alert
      dpDeactivateAlert( dsParentDPEs[x], bRetVal1 );
      if( !bRetVal1 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpDeactivateAlert FOR DPE '" + dsParentDPEs[x] + "'!!" );
      }
        

      // Now change the sumalert dplist
      iRetVal = dpSet( dsParentDPEs[x] + ":_alert_hdl.._dp_list",    dsChildDPEs,
                        dsParentDPEs[x] + ":_alert_hdl.._dp_pattern", "" );

      dyn_errClass derrLastError = getLastError();
      if( dynlen(derrLastError) > 0 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpSet FOR DPE, getLastError():", derrLastError );
      }
      else if( iRetVal != 0 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpSet FOR DPE, iRetVal = " + iRetVal );
      }
  
      // Activate alert again
      dpActivateAlert( dsParentDPEs[x], bRetVal2 );
      if( !bRetVal2 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpActivateAlert FOR DPE '" + dsParentDPEs[x] + "'!!" );
      }

      // Show if we're succesfull
      if( bRetVal1 && bRetVal2 && ( iRetVal == 0 ) && bDebug )
      {
        DebugTN( "setSumAlerts(): SumAlerts for DPE '" + dsParentDPEs[x] + "' succesfully set to " + dynlen(dsChildDPEs) + " child DPEs" );
      }
        
    }
    else
    {
      DebugTN( "setSumAlerts(): DPE '" + dsParentDPEs[x] + "' DOESN'T HAVE AN ALERT-HANDLE OR NOT OF TYPE SUM-ALERT!!" );
    }
    
    // Small delay to give some time and limit number of events
    delay(0,10);
    
  }
  
  // If this system is the MCU: call function for MCU alerts
  if( getSystemName() == MainDBName )
  {
    setSumAlerts_MCU();
  }
  
  dpSet( "scriptInfo.setSumAlerts.runDone", true );
  DebugTN("setSumAlerts.ctl:main|set of sumAlerts done");     
  
}




void setSumAlerts_MCU()
{
  int x, y;
  string strDPE, strParentDP;
  dyn_string dsParentDPEs, dsChilds, dsChildDPEs, dsParentRelations;

  
  DebugTN("setSumAlerts_MCU.ctl:main|start set of sumAlerts");     
    
  // Get all DPE's with a 'childSumAlert'
  dsParentDPEs = dpNames( "*.status.childSumAlert", "Station" );

  dynSort(dsParentDPEs);
  
  // Go through sumalerts
  for( x=1; x<=dynlen(dsParentDPEs); x++ )
  {
    bool bRetVal1, bRetVal2;
    int iRetVal, iAlertHdlType;
    string strDPE;
    dyn_string dsChildDPEs;
    
    strParentDP = dpSubStr( dsParentDPEs[x], DPSUB_DP );
    strDPE = dpSubStr( dsParentDPEs[x], DPSUB_DP_EL );
    
    
    // Skip master datapoints 
    if( patternMatch( "*_mp*", strDPE ))
    {
      continue;
    }
    
    if( strDPE == "" )
    {
      continue;
    }


    if (bDebug) 
    {
      DebugTN( __FUNCTION__ + "(), working on: " + strDPE );
    }

    // Define DPE for childsumalert: this is the determined dist_childsumalert
    dynClear( dsChildDPEs );
    dsChildDPEs[1] = strParentDP + ".dist_childSumAlert";

    
    // Check if this DPE has an alert_hdl of type sumalert
    dpGet( dsParentDPEs[x] + ":_alert_hdl.._type", iAlertHdlType );
    
    if( iAlertHdlType == DPCONFIG_SUM_ALERT)
    {
      // First deactivate the alert
      dpDeactivateAlert( dsParentDPEs[x], bRetVal1 );
      if( !bRetVal1 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpDeactivateAlert FOR DPE '" + dsParentDPEs[x] + "'!!" );
      }
        
      // If list is empty: use dummybit
      if( dynlen(dsChildDPEs) <= 0 )
      {
         DebugTN( "setSumAlerts(): empty dsChildDPEs list for DPE '" + dsParentDPEs[x] + "', 'DummyBit' will be used !!" );
        dsChildDPEs = makeDynString( "DummyBit." );
      }

      // Now change the sumalert dplist
      iRetVal = dpSet( dsParentDPEs[x] + ":_alert_hdl.._dp_list",    dsChildDPEs,
                        dsParentDPEs[x] + ":_alert_hdl.._dp_pattern", "" );

      dyn_errClass derrLastError = getLastError();
      if( dynlen(derrLastError) > 0 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpSet FOR DPE, getLastError():", derrLastError );
      }
      else if( iRetVal != 0 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpSet FOR DPE, iRetVal = " + iRetVal );
      }

      // Activate alert again
      dpActivateAlert( dsParentDPEs[x], bRetVal2 );
      if( !bRetVal2 )
      {
        DebugTN( "setSumAlerts(): FAILED TO dpActivateAlert FOR DPE '" + dsParentDPEs[x] + "'!!" );
      }

      // Show if we're succesfull
      if( bRetVal1 && bRetVal2 && ( iRetVal == 0 ) && bDebug )
      {
         DebugTN( "setSumAlerts(): SumAlerts for DPE '" + dsParentDPEs[x] + "' succesfully set to " + dynlen(dsChildDPEs) + " child DPEs" );
      }
        
    }
    else
    {
      DebugTN( "setSumAlerts(): DPE '" + dsParentDPEs[x] + "' DOESN'T HAVE AN ALERT-HANDLE OR NOT OF TYPE SUM-ALERT!!" );
    }
    
    // Small delay to give some time and limit number of events
    delay(0,10);
    
  }
  
}


private dyn_string GetChilds( string strDPE )
{
  int x, iLevel;
  string strDP, strParent, strChildDP, strChildDPE;
  dyn_string dsDPEs, dsChilds;

  strParent = strDPE;
  
  strDP = dpSubStr( strDPE, DPSUB_DP );
  strDPE = dpSubStr( strDPE, DPSUB_DP_EL );
  
  iLevel = GetDpeLevel( strDPE );
    
  // Get childs of this DPE  
  if( patternMatch( "*.*", strDPE ) )
  {
    // Only get child DPE's
    dynAppend( dsDPEs, dpNames( strDPE + ".**.childSumAlert" ) );
  }
  else
  {
    // Get child DP's and child DPE's
    dynAppend( dsDPEs, dpNames( strDP + "_*.*.childSumAlert" ) );
    dynAppend( dsDPEs, dpNames( strDPE + ".**.childSumAlert" ) );
  }
    
  
  for( x=dynlen(dsDPEs); x>=1; x-- )
  {
    strChildDP  = dpSubStr( dsDPEs[x], DPSUB_DP );
    strChildDPE = dpSubStr( dsDPEs[x], DPSUB_DP_EL );
    strChildDPE = RemoveLastDpeParts(strChildDPE);

    // Remove master datapoints    
    if( patternMatch( "*_mp*", strChildDPE ) )
    {
      continue;
    }
    
    
    if( GetDpeLevel( strChildDPE ) <= 1 )
    {    
      // If this DP is not a direct child, but a childs child, skip it
      if( patternMatch( strParent + "_*_*", strChildDPE ) )
      {
        continue;
      }
    }
    else
    {
      // Check level of this DPE, if more then 2 deeper then given leven, skip it (so only next level is used)
      if( GetDpeLevel( strChildDPE ) > ( iLevel + 1 ) )
      {
        continue;
      }
    }
      
    // Remove our given DPE
    if( strChildDPE == strDPE )
    {
      continue;
    }
    
    // The antenna's should not be recognized as children based on name (they have their own reference to RCUx/y)
    if( ( dpTypeName(strChildDP) == "HBAAntenna" ) ||
        ( dpTypeName(strChildDP) == "LBAAntenna" ) )
    {
      continue;
    }
    
    dynAppend( dsChilds, strChildDPE );
    
  }

  
  dynUnique( dsChilds );
  dynSort( dsChilds );
  
  return dsChilds;
}



private dyn_string GetChildDPEs( string strDPE )
{
  int x, iLevel;
  dyn_string dsDPEs, dsChildDPEs;
  
  iLevel = GetDpeLevel(strDPE);

  // Get 'state' and 'childSumAlert' DPE  
  dynAppend( dsDPEs, dpNames( strDPE + ".*.state" ) );
  dynAppend( dsDPEs, dpNames( strDPE + ".*.childSumAlert" ) );
  
  // Only append DPE's if they are 2 levels deeper then given DPE
  for( x=1; x<=dynlen(dsDPEs); x++ )
  {
    dsDPEs[x] = dpSubStr( dsDPEs[x], DPSUB_DP_EL );
    
    if( GetDpeLevel(dsDPEs[x]) == ( iLevel + 2 ) )
    {
      dynAppend( dsChildDPEs, dsDPEs[x] );
    }
    
  }

  return dsChildDPEs;
}


private string RemoveLastDpeParts( string strDPE )
{
  dyn_string dsParts;
  
  strDPE = dpSubStr( strDPE, DPSUB_DP_EL );
  
  // Split into parts
  dsParts = strsplit( strDPE, "." );

  // Remove 'first' last part
  if( dynlen( dsParts ) >= 2 )
  {
    dynRemove( dsParts, dynlen(dsParts) );
  }
    
  // Remove 'second' last part
  if( dynlen( dsParts ) >= 2 )
  {
    dynRemove( dsParts, dynlen(dsParts) );
  }
    
  // Convert back to DPE
  strDPE = dynStringToString( dsParts, "." );
  
  return strDPE;
}





private int GetDpeLevel( string strDPE )
{
  dyn_string dsParts;
  
  strDPE = dpSubStr( strDPE, DPSUB_DP_EL );
  
  dsParts = strsplit( strDPE, "." );
  
  // This is a DPE?
  if( dynlen(dsParts) <= 1 )
    return 0;
        
  return ( dynlen(dsParts) - 1 );
}




private dyn_string GetRelationsToParent( string strParentDP )
{
  int x;
  string strQuery, strDP;
  dyn_dyn_anytype ddaData;
  dyn_string dsParentRelations;
  
  
  strQuery = "SELECT '_original.._value' FROM '{*.common.RCUX,*.common.RCUY}' WHERE '_original.._value' LIKE \"" + strParentDP + ".*\" OR '_original.._value'  LIKE \"" + strParentDP + "\"";
  
  dpQuery( strQuery, ddaData );
   
//  if( dynlen(ddaData) >= 2 )
//    DebugTN( __FUNCTION__ + "(): strParentDP = " + strParentDP, ddaData );
  
  for( x=2; x<=dynlen(ddaData); x++ )
  {
    // Determine DP-name and add to dyn_string with relations to given parent-DP
    strDP = dpSubStr( ddaData[x][1], DPSUB_DP );
    dynAppend( dsParentRelations, strDP );
  }
  
  dynUnique( dsParentRelations );

  if( bDebug && ( dynlen(dsParentRelations) > 0 ) )
  {
    DebugTN( __FUNCTION__ + "(): strParentDP = '" + strParentDP + "' related DPs: " + dynStringToString( dsParentRelations, "," )  );
  }
  
  return dsParentRelations;
}
