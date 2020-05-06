//# AzEl.cc: Azimuth and elevation for a direction (ra, dec) on the sky.
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

#include <BBSKernel/Expr/AzEl.h>
#include <Common/LofarLogger.h>

#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MCPosition.h>
#include <casacore/measures/Measures/MeasFrame.h>
#include <casacore/measures/Measures/MeasConvert.h>
#include <casacore/casa/Quanta/Quantum.h>

namespace LOFAR
{
namespace BBS
{

AzEl::AzEl(const casacore::MPosition &position,
    const Expr<Vector<2> >::ConstPtr &direction)
    :   BasicUnaryExpr<Vector<2>, Vector<2> >(direction),
        itsPosition(casacore::MPosition::Convert(position, casacore::MPosition::ITRF)())
{
}

const Vector<2>::View AzEl::evaluateImpl(const Grid &grid,
    const Vector<2>::View &direction) const
{
    // Check preconditions.
    ASSERTSTR(!direction(0).isArray() && !direction(1).isArray(), "Variable"
        " source directions not supported (yet).");
    ASSERTSTR(!direction(0).isComplex() && !direction(1).isComplex(), "Source"
        " directions should be real valued.");

    casacore::Quantum<casacore::Double> qEpoch(0.0, "s");
    casacore::MEpoch mEpoch(qEpoch, casacore::MEpoch::UTC);

    // Create and initialize a frame.
    casacore::MeasFrame frame;
    frame.set(itsPosition);
    frame.set(mEpoch);

    // Create conversion engine.
    casacore::MDirection mDirection(casacore::MVDirection(direction(0).getDouble(),
        direction(1).getDouble()),
        casacore::MDirection::Ref(casacore::MDirection::J2000));

    // TODO: Do we need to use AZEL or AZELGEO here?
//    casacore::MDirection::Convert converter = casacore::MDirection::Convert(mDirection,
//        casacore::MDirection::Ref(casacore::MDirection::AZEL, frame));
    casacore::MDirection::Convert converter = casacore::MDirection::Convert(mDirection,
        casacore::MDirection::Ref(casacore::MDirection::AZELGEO, frame));

    // Allocate space for the result.
    // TODO: This is a hack! The Matrix class does not support 1xN or Nx1
    // "matrices".
    const size_t nTime = grid[TIME]->size();

    Matrix az, el;
    double *az_p = az.setDoubleFormat(1, nTime);
    double *el_p = el.setDoubleFormat(1, nTime);

    // Compute (az, el) coordinates.
    for(size_t i = 0; i < nTime; ++i)
    {
        // Update reference frame.
        const double time = grid[TIME]->center(i);

        qEpoch.setValue(time);
        mEpoch.set(qEpoch);
        frame.set(mEpoch);

        // Compute azimuth and elevation.
        casacore::MVDirection mvAzel(converter().getValue());
        const casacore::Vector<casacore::Double> azel =
            mvAzel.getAngle("rad").getValue();
        *az_p++ = azel(0);
        *el_p++ = azel(1);
    }


    Vector<2>::View result;
    result.assign(0, az);
    result.assign(1, el);

    return result;
}

} //# namespace BBS
} //# namespace LOFAR
