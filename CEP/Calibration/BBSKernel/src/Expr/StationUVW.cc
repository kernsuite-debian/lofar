//# StationUVW.cc: Station UVW coordinates.
//#
//# Copyright (C) 2009
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id$

#include <lofar_config.h>
#include <BBSKernel/Expr/StationUVW.h>

#include <casacore/measures/Measures/MBaseline.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MeasFrame.h>
#include <casacore/measures/Measures/MeasConvert.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/Measures/MCPosition.h>
#include <casacore/measures/Measures/MCBaseline.h>
#include <casacore/casa/Quanta/MVuvw.h>

namespace LOFAR
{
namespace BBS
{

StationUVW::StationUVW(const casacore::MPosition &arrayPosition,
    const casacore::MPosition &stationPosition,
    const casacore::MDirection &direction)
    :   itsArrayPosition(casacore::MPosition::Convert(arrayPosition,
            casacore::MPosition::ITRF)()),
        itsStationPosition(casacore::MPosition::Convert(stationPosition,
            casacore::MPosition::ITRF)()),
        itsDirection(casacore::MDirection::Convert(direction,
            casacore::MDirection::J2000)())
{
}

const Vector<3> StationUVW::evaluateExpr(const Request &request, Cache&,
    unsigned int grid) const
{
    EXPR_TIMER_START();

    // Initialize reference frame.
    casacore::Quantum<casacore::Double> qEpoch(0.0, "s");
    casacore::MEpoch mEpoch(qEpoch, casacore::MEpoch::UTC);
    casacore::MeasFrame mFrame(mEpoch, itsArrayPosition, itsDirection);

    // Use baseline coordinates relative to the array reference position (to
    // keep values small). The array reference position will drop out when
    // computing baseline UVW coordinates from a pair of "station" UVW
    // coordinates.
    casacore::MVBaseline mvBaseline(itsStationPosition.getValue(),
        itsArrayPosition.getValue());
    casacore::MBaseline mBaseline(mvBaseline,
        casacore::MBaseline::Ref(casacore::MBaseline::ITRF, mFrame));

    // Setup coordinate transformation engine.
    casacore::MBaseline::Convert convertor(mBaseline, casacore::MBaseline::J2000);

    // Allocate space for the result.
    // TODO: This is a hack! The Matrix class does not support 1xN or Nx1
    // "matrices".
    Axis::ShPtr timeAxis(request[grid][TIME]);
    const size_t nTime = timeAxis->size();

    Matrix U, V, W;
    double *u = U.setDoubleFormat(1, nTime);
    double *v = V.setDoubleFormat(1, nTime);
    double *w = W.setDoubleFormat(1, nTime);

    // Compute UVW coordinates.
    for(size_t i = 0; i < nTime; ++i)
    {
        // Update reference frame.
        qEpoch.setValue(timeAxis->center(i));
        mEpoch.set(qEpoch);
        mFrame.set(mEpoch);

        // Compute UVW coordinates (J2000).
        casacore::MBaseline mBaselineJ2000(convertor());
        casacore::MVuvw mvUVW(mBaselineJ2000.getValue(), itsDirection.getValue());

        *u++ = mvUVW(0);
        *v++ = mvUVW(1);
        *w++ = mvUVW(2);
    }

    Vector<3> result;
    result.assign(0, U);
    result.assign(1, V);
    result.assign(2, W);

    EXPR_TIMER_STOP();

    return result;
}

} //# namespace BBS
} //# namespace LOFAR
