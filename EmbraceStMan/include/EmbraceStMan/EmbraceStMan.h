//# EmbraceStMan.h: Storage Manager for the main table of an EMBRACE MS
//# Copyright (C) 2009
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR software suite.
//# The LOFAR software suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published
//# by the Free Software Foundation, either version 3 of the License, or
//# (at your option) any later version.
//#
//# The LOFAR software suite is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along
//# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
//#
//# $Id$

#ifndef EMBRACE_EMBRACESTMAN_EMBRACESTMAN_H
#define EMBRACE_EMBRACESTMAN_EMBRACESTMAN_H

//# Includes
#include <casacore/tables/DataMan/DataManager.h>
#include <casacore/casa/IO/LargeFiledesIO.h>
#include <casacore/casa/Containers/Block.h>
#include <casacore/casa/Containers/Record.h>
#include <vector>

namespace EMBRACE {

//# Forward Declarations.
class EmbraceColumn;

// <summary>
// The Storage Manager for the main table of a raw EMBRACE MS
// </summary>

// <use visibility=export>

// <reviewed reviewer="UNKNOWN" date="before2004/08/25" tests="tEmbraceStMan.cc">
// </reviewed>

// <prerequisite>
//# Classes you should understand before using this one.
//   <li> The Table Data Managers concept as described in module file
//        <linkto module="Tables:Data Managers">Tables.h</linkto>
// </prerequisite>

// <etymology>
// EmbraceStMan is the data manager which stores the data for an EMBRACE MS.
// </etymology>

// <synopsis>
// EmbraceStMan is a specific storage manager for the main table of an EMBRACE MS.
// For performance purposes the raw data from the correlator is directly
// written to a disk file. However, to be able to use the data directly as a
// MeasurementSet, this specific storage manager is created offering access to
// all mandatory columns in the main table of the MS.
//
// Similar to other storage managers, the EmbraceStMan files need to be part of
// the table directory. There are two files:
// <ul>
//  <li> The meta file contains the meta data describing baselines, start time,
//       integration time, etc. It needs to be written as an AipsIO file.
//       The meta info should also tell the endianness of the data file.
//  <li> The data file consists of NSEQ data blocks each containing:
//   <ul>
//    <li> 4-byte sequence number defining the time stamp.
//    <li> Complex data with shape [npol,nchan,nbasel].
//    <li> Unsigned short nr of samples used in each data point. It has shape
//         [nchan,nbasel]. It defines WEIGHT_SPECTRUM and FLAG.
//    <li> Filler bytes to align the blocks as given in the meta info.
//   </ul>
//   The sequence numbers are ascending, but there can be holes due to
//   missing time stamps.
// </ul>
// The first versions of the data file can only handle regularly shaped data
// with equal integration times. A future version might be able to deal with
// varying integration times (depending on baseline length).
//
// Most of the MS columns (like DATA_DESC_ID) are not stored in the data file;
// usually they map to the value 0. This is also true for the UVW column, so
// the UVW coordinates need to be added to the table in a separate step because
// the online system does not have the resources to do it.
//
// All columns are readonly with the exception of DATA.
// </synopsis>

// <motivation>
// The common Table storage managers are too slow for the possibly high
// output rate of the EMBRACE correlator.
// </motivation>

// <example>
// The following example shows how to create a table and how to attach
// the storage manager to some columns.
// <srcblock>
//   SetupNewTable newtab("name.data", tableDesc, Table::New);
//   EmbraceStMan stman;                     // define storage manager
//   newtab.bindColumn ("DATA", stman);    // bind column to st.man.
//   newtab.bindColumn ("FLAG", stman);    // bind column to st.man.
//   Table tab(newtab);                    // actually create table
// </srcblock>
// </example>

//# <todo asof="$DATE:$">
//# A List of bugs, limitations, extensions or planned refinements.
//# </todo>


class EmbraceStMan : public casacore::DataManager
{
public:
    // Create an Embrace storage manager with the given name.
    // If no name is used, it is set to "EmbraceStMan"
  explicit EmbraceStMan (const casacore::String& dataManagerName = "EmbraceStMan");

  // Create an Embrace storage manager with the given name.
  // The specifications are part of the record (as created by dataManagerSpec).
  EmbraceStMan (const casacore::String& dataManagerName, const casacore::Record& spec);
  
  ~EmbraceStMan();

  // Clone this object.
  virtual casacore::DataManager* clone() const;
  
  // Get the type name of the data manager (i.e. EmbraceStMan).
  virtual casacore::String dataManagerType() const;
  
  // Get the name given to the storage manager (in the constructor).
  virtual casacore::String dataManagerName() const;
  
  // Record a record containing data manager specifications.
  virtual casacore::Record dataManagerSpec() const;

  // Get the number of rows in this storage manager.
  casacore::uInt getNRow() const
    { return itsNrRows; }
  
  // The storage manager cannot add rows.
  virtual casacore::Bool canAddRow() const;
  
  // The storage manager cannot delete rows.
  virtual casacore::Bool canRemoveRow() const;
  
  // The storage manager can add columns, which does not really do something.
  virtual casacore::Bool canAddColumn() const;
  
  // Columns can be removed, but it does not do anything at all.
  virtual casacore::Bool canRemoveColumn() const;
  
  // Make the object from the type name string.
  // This function gets registered in the DataManager "constructor" map.
  // The caller has to delete the object.
  static casacore::DataManager* makeObject (const casacore::String& aDataManType,
                                        const casacore::Record& spec);

  // Register the class name and the static makeObject "constructor".
  // This will make the engine known to the table system.
  static void registerClass();


  // Get data.
  // <group>
  const casacore::Block<casacore::Int>& ant1() const
    { return itsAnt1; }
  const casacore::Block<casacore::Int>& ant2() const
    { return itsAnt2; }
  double time (casacore::uInt blocknr);
  double interval() const
    { return itsTimeIntv; }
  casacore::uInt nchan() const
    { return itsNChan; }
  casacore::uInt npol() const
    { return itsNPol; }
  void getData (casacore::uInt rownr, casacore::Complex* buf);
  void putData (casacore::uInt rownr, const casacore::Complex* buf);
  // </group>

  casacore::uInt getEmbraceStManVersion() const
    { return itsVersion; }

private:
  // Copy constructor cannot be used.
  EmbraceStMan (const EmbraceStMan& that);

  // Assignment cannot be used.
  EmbraceStMan& operator= (const EmbraceStMan& that);
  
  // Flush and optionally fsync the data.
  // It does nothing, and returns False.
  virtual casacore::Bool flush (casacore::AipsIO&, casacore::Bool doFsync);
  
  // Let the storage manager create files as needed for a new table.
  // This allows a column with an indirect array to create its file.
  virtual void create (casacore::uInt nrrow);
  
  // Open the storage manager file for an existing table.
  // Return the number of rows in the data file.
  // <group>
  virtual void open (casacore::uInt nrrow, casacore::AipsIO&); //# should never be called
  virtual casacore::uInt open1 (casacore::uInt nrrow, casacore::AipsIO&);
  // </group>

  // Prepare the columns (needed for UvwColumn).
  virtual void prepare();

  // Resync the storage manager with the new file contents.
  // It does nothing.
  // <group>
  virtual void resync (casacore::uInt nrrow);   //# should never be called
  virtual casacore::uInt resync1 (casacore::uInt nrrow);
  // </group>
  
  // Reopen the storage manager files for read/write.
  // It does nothing.
  virtual void reopenRW();
  
  // The data manager will be deleted (because all its columns are
  // requested to be deleted).
  // So clean up the things needed (e.g. delete files).
  virtual void deleteManager();

  // Add rows to the storage manager.
  // It cannot do it, so throws an exception.
  virtual void addRow (casacore::uInt nrrow);
  
  // Delete a row from all columns.
  // It cannot do it, so throws an exception.
  virtual void removeRow (casacore::uInt rowNr);
  
  // Do the final addition of a column.
  // It won't do anything.
  virtual void addColumn (casacore::DataManagerColumn*);
  
  // Remove a column from the data file.
  // It won't do anything.
  virtual void removeColumn (casacore::DataManagerColumn*);
  
  // Create a column in the storage manager on behalf of a table column.
  // The caller has to delete the newly created object.
  // <group>
  // Create a scalar column.
  virtual casacore::DataManagerColumn* makeScalarColumn (const casacore::String& aName,
					       int aDataType,
					       const casacore::String& aDataTypeID);
  // Create a direct array column.
  virtual casacore::DataManagerColumn* makeDirArrColumn (const casacore::String& aName,
					       int aDataType,
					       const casacore::String& aDataTypeID);
  // Create an indirect array column.
  virtual casacore::DataManagerColumn* makeIndArrColumn (const casacore::String& aName,
					       int aDataType,
					       const casacore::String& aDataTypeID);
  // </group>

  // Initialize by reading the header info.
  void init();

  // Open the data file and seqnr file.
  // The seqnr is always memory-mapped (it is very small).
  // The data file is only memory-mapped in 64 bit systems because the
  // address space of 32-bit systems is too small for it.
  void openFile (bool writable);

  //# Declare member variables.
  // Name of data manager.
  casacore::String itsDataManName;
  // The name of the data file.
  casacore::String itsFileName;
  // The number of rows in the columns.
  casacore::uInt         itsNrRows;
  // The antennae forming the baselines.
  casacore::Block<casacore::Int> itsAnt1;
  casacore::Block<casacore::Int> itsAnt2;
  // The start time and interval.
  double itsStartTime;
  double itsTimeIntv;
  casacore::uInt itsNChan;
  casacore::uInt itsNPol;
  // The column objects.
  std::vector<EmbraceColumn*> itsColumns;
  // Regular IO is used.
  casacore::LargeFiledesIO* itsRegFile;
  casacore::Block<float> itsBuffer;  //# buffer of size itsBLDataSize for regular IO
  // The seqnr file (if present) is always memory-mapped because it is small.
  bool   itsDoSwap;       //# True = byte-swapping is needed
  casacore::Int64  itsBLDataSize;    //# data size (in bytes) of a single baseline
  casacore::Record itsSpec;

  casacore::uInt itsVersion;         //# Version of EmbraceStMan MeasurementSet
};


} //# end namespace

#endif
