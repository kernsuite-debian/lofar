// claimManager.ctl
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
// claimManager functions
///////////////////////////////////////////////////////////////////
//
// Functions and procedures
//
// claimManager_nameToRealName		         : returns the DPname of the actual datapoint
// claimManager_queryConnectClaims         : Establish a query connect to get all claimed datapoints
// claimManager_queryConnectClaim_Callback : Callback for the above query connect

#uses "GCFCommon.ctl"

// the name of the datapoints plus the actual name
// This is used to quickly determine the name of the real datapoint
// from the graphical user interface
global dyn_string strClaimDPName;               // datapoint that was claimed
global dyn_string strClaimObjectName;           // Actual object name
global int        g_freeClaims = 0;             // keeps track of free claims
global int        g_usedClaims = 0;             // keeps track of used claims
global int        g_unusedClaims = 0;           // keeps track of unused claims


// ****************************************
// Name : claimManager_nameToRealName
// ****************************************
// Description:
//    Accepts a name and will return:
//
//    1)  The name of the datapoint
//        Example:  'LOFAR" -> 'LOFAR'
//
//    2)  The name of the actual 'Claimed' datapoint
//        when the name refers to a temporary datapoint
//
// Returns:
//    The DP name of the actual datapoint
//
// Restrictions:
//    The 'Claimed' objects have a name
// ***************************************

string claimManager_nameToRealName( string strName )
{
  if( dpExists( strName ))       // When the name refers to an actual datapoint
    return strName;              // then just return that name
  
  // Do we know the 'Claimed' name
  int iPos = dynContains( strClaimObjectName, strName );
  
  if( iPos < 1 )
    return "";
  else
     return strClaimDPName[ iPos ];

}

// ****************************************
// Name : claimManager_realNameToName
// ****************************************
// Description:
//    Accepts a temp datapoint and will return:
//
//    1)  The name of the datapoint
//        Example:  'LOFAR" -> 'LOFAR'
//
//    2)  The name of the actual 'Claimed' datapoint
//        when the name refers to a temporary datapoint
//
// Returns:
//    The DP name of the claimed datapoint
//
// Restrictions:
//    The 'Claimed' objects have a name
// ***************************************

string claimManager_realNameToName( string strName )
{
  // Do we know the 'Claimed' name
  int iPos = dynContains( strClaimDPName, dpSubStr(strName,DPSUB_DP) );
  
  if( iPos < 1 )
    return "";
  else
     return strClaimObjectName[ iPos ];

}

// ****************************************
// Name : claimManager_queryConnectClaims
// ****************************************
// Description:
//    Establish a query connect to get all
//    claimed datapoints
//
// Returns:
//    None
// ***************************************

void claimManager_queryConnectClaims()
{
  string baseDP = MainDBName+"ClaimManager.cache";
  if (dpExists(baseDP)) {
    if (dpConnect("claimManager_updateCacheClaims",true, baseDP + ".newObjectNames:_online.._value",
                                                         baseDP + ".DPNames:_online.._value",
                                                         baseDP + ".claimDates:_online.._value",
                                                         baseDP + ".freeDates:_online.._value",
                                                         baseDP + ".newObjectNames:_online.._invalid") == -1)
    {
      LOG_DEBUG("Claim_Viewer.pnl:main|Couldn't connect to: "+baseDP);
    } 
    else
    {
      LOG_DEBUG("Claim_Viewer.pnl:main|Connected to: " + baseDP);
    }
  } 
  else
  {
    if (!isStandalone()) {
      LOG_ERROR( "claimManager.ctl:claimManager_queryConnectClaims|Couldn't find DP to connect to: "+baseDP);
    }
    if ( g_initializing )
    {
      writeInitProcess("connectClaimsFinished"); 
    }
  }
}

claimManager_updateCacheClaims(string dp1, dyn_string objectNames,
                               string dp2, dyn_string DPNames,
                               string dp3, dyn_time claimDates,
                               string dp4, dyn_time freeDates,
                               string dp5, bool invalid)
{
  dyn_string claimedObjectNames;
  dyn_string claimedDPNames;
  
  if (invalid)
  {
    LOG_WARN("claimManager.ctl:claimManager_updateCacheClaims|ClaimManager.cache is invalid");
    if ( g_initializing ) {
      writeInitProcess("connectClaimsFinished"); 
    }
    return;
  }

  int unused = 0;
  int claimed = 0;
  int freed = 0;

  for (int i=1; i<= dynlen(objectNames);i++)
  {
    time claim = claimDates[i];
    time free = freeDates[i];
    dynAppend(claimedObjectNames,objectNames[i]);
    dynAppend(claimedDPNames,DPNames[i]);
    if (period(claim) == 0 && period(free) == 0) 
    {
      unused += 1;
    }
    else if (period(claim) == 0)
    {
      freed += 1;
    }
    else if (period(free) == 0)
    {
      claimed += 1;
    }
    else
    {
      full = true;
    }
  }

  
  g_unusedClaims = unused;
  g_usedClaims = claimed;
  g_freeClaims = freed;

  strClaimDPName = claimedDPNames;
  strClaimObjectName = claimedObjectNames; 
                 
  LOG_DEBUG( "claimManager.ctl:claimManager_updateCacheClaims|writing connectClaimsFinished");
  if ( g_initializing ) {
    writeInitProcess("connectClaimsFinished"); 
  }
}
