//# Operation.h: Base class for awimager operations
//#
//# Copyright (C) 2014
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
//# $Id: $

#ifndef LOFAR_LOFARFT_OPERATION_H
#define LOFAR_LOFARFT_OPERATION_H

#include <AWImager2/Imager.h>

#include <Common/ObjectFactory.h>
#include <Common/Singleton.h>
#include <Common/lofar_string.h>

#include <casacore/casa/BasicSL/String.h>
#include <casacore/casa/Containers/Record.h>
#include <casacore/ms/MeasurementSets/MeasurementSet.h>


// Define color codes for help text

// #define COLOR_DEFAULT "\033[38;2;40;120;130m"
#define COLOR_DEFAULT "\033[36m"

// #define COLOR_OPERATION "\033[38;2;0;60;130m"
#define COLOR_OPERATION "\033[34m"

#define COLOR_PARAMETER "\033[35m"

#define COLOR_RESET "\033[0m"


namespace LOFAR { 
  
  namespace LofarFT {

    class Operation
    {
    public:
      Operation(ParameterSet& parset);
      
      virtual void init();

      void initData();

      void initImage();

      void initWeight();

      void initFTMachine();

      void makeEmptyImage(const casacore::String& imgName, casacore::Int fieldid);

      virtual void run() {}; // Only derived classes will do something useful in run()

      virtual void showHelp (ostream& os, const string& name);
      
      static casacore::IPosition readIPosition (const casacore::String& in);
      
      static casacore::Quantity readQuantity (const casacore::String& in);
      
      static casacore::MDirection readDirection (const casacore::String& in);
      
      static void readFilter (
        const casacore::String& filter,
        casacore::Quantity& bmajor, 
        casacore::Quantity& bminor, 
        casacore::Quantity& bpa);

      static void normalize(
        casacore::String imagename_in, 
        casacore::String avgpb_name, 
        casacore::String imagename_out);
      
    protected:
      ParameterSet               &itsParset;
      casacore::String               itsMSName;
      casacore::MeasurementSet       itsMS;
      casacore::CountedPtr<Imager>   itsImager;
      bool                       needsData;
      bool                       needsImage;
      bool                       needsFTMachine;
      bool                       needsWeight;

    private:
      void showHelpData (ostream& os, const string& name);
      void showHelpImage (ostream& os, const string& name);
      void showHelpFTMachine (ostream& os, const string& name);
      void showHelpWeight (ostream& os, const string& name);
      casacore::Double observationReferenceFreq(
        const casacore::MeasurementSet &ms,
        casacore::uInt idDataDescription);
    };

    // Factory that can be used to generate new Operation objects.
    // The factory is defined as a singleton.
    typedef Singleton< ObjectFactory< Operation*(ParameterSet&), string > > OperationFactory;

  } //# namespace LofarFT
} //# namespace LOFAR

#endif
