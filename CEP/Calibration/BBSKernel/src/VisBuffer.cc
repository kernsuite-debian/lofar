//# VisBuffer.cc: A buffer of visibility data and associated information (e.g.
//# flags, UVW coordinates).
//#
//# Copyright (C) 2007
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

#include <lofar_config.h>
#include <BBSKernel/VisBuffer.h>
#include <BBSKernel/Exceptions.h>
#include <BBSKernel/EstimateUtil.h>

#include <Common/lofar_algorithm.h>
#include <Common/LofarLogger.h>

#include <casacore/measures/Measures/MBaseline.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MeasFrame.h>
#include <casacore/measures/Measures/MeasConvert.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/Measures/MCPosition.h>
#include <casacore/measures/Measures/MCBaseline.h>
#include <casacore/casa/Quanta/MVuvw.h>
#include <casacore/casa/BasicSL/Complex.h>

namespace LOFAR
{
namespace BBS
{

VisBuffer::VisBuffer(const VisDimensions &dims, bool hasCovariance,
    bool hasFlags)
    :   itsDims(dims)
{
    size_t sample = sizeof(dcomplex);
    samples.resize(boost::extents[nBaselines()][nTime()][nFreq()]
        [nCorrelations()]);

    if(hasCovariance)
    {
        sample += nCorrelations() * sizeof(double);
        covariance.resize(boost::extents[nBaselines()][nTime()][nFreq()]
            [nCorrelations()][nCorrelations()]);
    }

    if(hasFlags)
    {
        sample += sizeof(flag_t);
        flags.resize(boost::extents[nBaselines()][nTime()][nFreq()]
            [nCorrelations()]);
    }

    LOG_DEBUG_STR("Buffer size: " << (nSamples() * sample) / (1024.0 * 1024.0)
        << " MB.");
}

void VisBuffer::setPhaseReference(const casacore::MDirection &reference)
{
    itsPhaseReference = casacore::MDirection::Convert(reference,
        casacore::MDirection::J2000)();
}

void VisBuffer::setDelayReference(const casacore::MDirection &reference)
{
    itsDelayReference = casacore::MDirection::Convert(reference,
        casacore::MDirection::J2000)();
}

void VisBuffer::setTileReference(const casacore::MDirection &reference)
{
    itsTileReference = casacore::MDirection::Convert(reference,
        casacore::MDirection::J2000)();
}

bool VisBuffer::isLinear() const
{
    for(size_t i = 0; i < nCorrelations(); ++i)
    {
        if(!Correlation::isLinear(correlations()[i]))
        {
            return false;
        }
    }

    return true;
}

bool VisBuffer::isCircular() const
{
    for(size_t i = 0; i < nCorrelations(); ++i)
    {
        if(!Correlation::isCircular(correlations()[i]))
        {
            return false;
        }
    }

    return true;
}

void VisBuffer::computeUVW()
{
    // For LOFAR MeasurementSets the UVW coordinates computed by this function
    // differ from the coordinates computed by the correlator only in the choice
    // of the reference position on earth. The correlator picks the position of
    // station N/2 as the reference position whereas here we use the centroid
    // of the station positions as the reference.

    // Ensure the UVW buffer is large enough.
    uvw.resize(boost::extents[nStations()][nTime()][3]);

    // Initialize reference frame.
    casacore::Quantum<casacore::Double> qEpoch(0.0, "s");
    casacore::MEpoch mEpoch(qEpoch, casacore::MEpoch::UTC);
    casacore::MeasFrame mFrame(mEpoch, itsInstrument->position(),
        itsPhaseReference);

    // Compute UVW.
    casacore::MVPosition mvArrayPosition = itsInstrument->position().getValue();
    for(size_t i = 0; i < nStations(); ++i)
    {
        // Use station positions relative to the array reference position (to
        // keep values small).
        casacore::MVPosition mvPosition =
            itsInstrument->station(i)->position().getValue();
        casacore::MVBaseline mvBaseline(mvPosition, mvArrayPosition);

        casacore::MBaseline mBaseline(mvBaseline,
            casacore::MBaseline::Ref(casacore::MBaseline::ITRF, mFrame));

        // Setup coordinate transformation engine.
        casacore::MBaseline::Convert convertor(mBaseline, casacore::MBaseline::J2000);

        // Compute UVW coordinates.
        for(size_t j = 0; j < nTime(); ++j)
        {
            qEpoch.setValue(grid()[TIME]->center(j));
            mEpoch.set(qEpoch);
            mFrame.set(mEpoch);

            // Create MVuvw from a baseline (MVBaseline) and a reference
            // direction (MVDirection). Baseline and reference direction are
            // _assumed_ to be in the same frame (see casacore documentation).
            casacore::MBaseline mBaselineJ2000(convertor());
            casacore::MVuvw mvUVW(mBaselineJ2000.getValue(),
                itsPhaseReference.getValue());

            uvw[i][j][0] = mvUVW(0);
            uvw[i][j][1] = mvUVW(1);
            uvw[i][j][2] = mvUVW(2);
        }
    }
}

void VisBuffer::flagsAndWithMask(flag_t mask)
{
    typedef boost::multi_array<flag_t, 4>::element* iterator;
    for(iterator it = flags.data(), end = flags.data() + flags.num_elements();
        it != end; ++it)
    {
        *it &= mask;
    }
}

void VisBuffer::flagsOrWithMask(flag_t mask)
{
    typedef boost::multi_array<flag_t, 4>::element* iterator;
    for(iterator it = flags.data(), end = flags.data() + flags.num_elements();
        it != end; ++it)
    {
        *it |= mask;
    }
}

void VisBuffer::flagsSet(flag_t value)
{
    typedef boost::multi_array<flag_t, 4>::element* iterator;
    for(iterator it = flags.data(), end = flags.data() + flags.num_elements();
        it != end; ++it)
    {
        *it = value;
    }
}

void VisBuffer::flagsNot()
{
    typedef boost::multi_array<flag_t, 4>::element* iterator;
    for(iterator it = flags.data(), end = flags.data() + flags.num_elements();
        it != end; ++it)
    {
        *it = ~(*it);
    }
}

void VisBuffer::flagsNaN()
{
    if(!hasFlags())
    {
        return;
    }

    typedef boost::multi_array<dcomplex, 4>::element* sample_iterator;
    typedef boost::multi_array<flag_t, 4>::element* flag_iterator;

    flag_iterator flag_it = flags.data();
    for(sample_iterator sample_it = samples.data(), sample_end = samples.data()
        + samples.num_elements(); sample_it != sample_end;)
    {
        // If any of the correlations is NaN, flag all correlations.
        for(size_t i = 0; i < nCorrelations(); i++)
        {
            if(casacore::isNaN(sample_it[i]))
            {
                for(size_t j = 0; j < nCorrelations(); j++)
                {
                    flag_it[j] |= 1;
                }

                break;
            }
        }
        flag_it += nCorrelations();
        sample_it += nCorrelations();
    }
}

} //# namespace BBS
} //# namespace LOFAR
