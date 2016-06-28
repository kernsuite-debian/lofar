//# SlidingFlagger.h: DPPP step class to flag data using rficonsole's functionality
//# Copyright (C) 2010
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
//# $Id: SlidingFlagger.h 26900 2013-10-08 20:12:58Z loose $
//#
//# @author Ger van Diepen

#ifndef DPPP_AOFLAG_SLIDINGFLAGGER_H
#define DPPP_AOFLAG_SLIDINGFLAGGER_H

// @file
// @brief DPPP step class to flag using rficonsole's functionality

#include <DPPP/DPInput.h>
#include <DPPP/DPBuffer.h>
#include <DPPP/FlagCounter.h>
#include <Common/lofar_vector.h>
#include <Common/lofar_smartptr.h>

#include <aoflagger.h>

namespace LOFAR {

  class ParameterSet;

  namespace DPPP {
    // @ingroup NDPPP

    // This class is a DPStep class flagging data points based on the
    // aoflagger library written by Andre Offringa.
    // See the following papers for background information:
    // <ul>
    // <li> Post-correlation radio frequency interference classification
    //      methods -- http://arxiv.org/abs/1002.1957 
    // <li> A LOFAR RFI detection pipeline and its first results
    //      -- http://arxiv.org/abs/1007.2089
    // </ul>
    //
    // When a correlation is flagged, all correlations for that data point
    // are flagged. It is possible to specify which correlations have to be
    // taken into account when flagging. Using, say, only XX may boost
    // performance with a factor 4, but miss points to be flagged.
    // It is also possible to specify the order in which the correlations
    // have to be tested.
    //
    // It is possible to flag specific baselines only using a selection on
    // baseline length.
    // <br>Furthermore it is possible to only flag the autocorrelations and
    // apply the resulting flags to the crosscorrelations, possibly selected
    // on baseline length.

    class SlidingFlagger: public DPStep
    {
    public:
      // Construct the object.
      // Parameters are obtained from the parset using the given prefix.
      SlidingFlagger (DPInput*, const ParameterSet&, const string& prefix);

      virtual ~SlidingFlagger();

      // Create an SlidingFlagger object using the given parset.
      static DPStep::ShPtr makeStep (DPInput*, const ParameterSet&,
                                     const std::string&);

      // Process the data.
      // When processed, it invokes the process function of the next step.
      virtual bool process (const DPBuffer&);

      // Finish the processing of this step and subsequent steps.
      virtual void finish();

      // Update the general info.
      // It is used to adjust the parms if needed.
      virtual void updateInfo (const DPInfo&);

      // Show the step parameters.
      virtual void show (std::ostream&) const;

      // Show the flagger counts.
      virtual void showCounts (std::ostream&) const;

      // Show the timings.
      virtual void showTimings (std::ostream&, double duration) const;

    private:
      struct ThreadData {
        FlagCounter flagCounter;
        NSTimer     moveTimer;
        NSTimer     flagTimer;
      };

      // Flag all baselines in the time window (using OpenMP to parallellize).
      // Process the buffers in the next step.
      void flag();

      // Flag a single baseline using the rfistrategy.
      void flagBaseline (uint bl, ThreadData&);

      // Fill the rfi strategy.
      void fillStrategy();

      //# Data members.
      string           itsName;
      uint             itsBufIndex;
      uint             itsNTimes;
      uint             itsNThreads;
      string           itsStrategyName;
      uint             itsWindowSize;
      uint             itsBufferSize;
      double           itsMemoryNeeded;  //# Memory needed for data/flags
      bool             itsPulsarMode;
      bool             itsPedantic;
      bool             itsDoAutoCorr;
      vector<DPBuffer> itsBuf;
      NSTimer          itsTimer;
      NSTimer          itsComputeTimer;  //# move/flag timer
      mutable FlagCounter   itsFlagCounter;
      vector<ThreadData>    itsTD;
      casa::Vector<double>  itsFreqs;
      aoflagger::AOFlagger  itsAOFlagger;
      boost::scoped_ptr<aoflagger::Strategy> itsStrategy;
    };

  } //# end namespace
}

#endif
