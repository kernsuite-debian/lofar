//# LofarATermOld.h: Compute the LOFAR beam response on the sky.
//#
//# Copyright (C) 2011
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

#ifndef LOFAR_LOFARFT_LOFARATERMOLD_H
#define LOFAR_LOFARFT_LOFARATERMOLD_H

#include <Common/LofarTypes.h>
#include <Common/lofar_map.h>
#include <Common/lofar_vector.h>

#include <casacore/casa/Arrays/Array.h>
#include <casacore/casa/BasicSL/String.h>
#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MDirection.h>

namespace casacore
{
  class DirectionCoordinate;
  class MEpoch;
  class MeasurementSet;
  class Path;
}

namespace LOFAR
{
  struct Vector3
  {
    const double &operator[](uint i) const
    { return __data[i]; }

    double &operator[](uint i)
    { return __data[i]; }

    double  __data[3];
  };

  class AntennaField
  {
  public:
    enum Axis
    {
      P,
      Q,
      R,
      N_Axis
    };

    struct Element
    {
      Vector3 offset;
      bool    flag[2];
    };

    AntennaField()
    {
    }

    AntennaField(const casacore::String &name, const Vector3 &position,
                 const Vector3 &p,
                 const Vector3 &q, const Vector3 &r);

    const casacore::String &name() const;
    const Vector3 &position() const;
    const Vector3 &axis(Axis axis) const;

    bool isHBA() const;

    void appendTileElement(const Vector3 &offset);
    inline uint nTileElement() const;
    inline const Vector3 &tileElement(uint i) const;

    void appendElement(const Element &element);
    inline uint nElement() const;
    inline const Element &element(uint i) const;

  private:
    casacore::String    m_name;
    Vector3         m_position;
    Vector3         m_axes[N_Axis];
    vector<Vector3> m_tileElements;
    vector<Element> m_elements;
  };

  class Station
  {
  public:
    Station()
    {
    }

    Station(const casacore::String &name, const casacore::MPosition &position);
    Station(const casacore::String &name, const casacore::MPosition &position,
            const AntennaField &field0);
    Station(const casacore::String &name, const casacore::MPosition &position,
            const AntennaField &field0, const AntennaField &field1);

    const casacore::String &name() const;
    const casacore::MPosition &position() const;

    bool isPhasedArray() const;
    uint nField() const;
    const AntennaField &field(uint i) const;

  private:
    casacore::String            m_name;
    casacore::MPosition         m_position;
    vector<AntennaField>    m_fields;
  };

  class Instrument
  {
  public:
    Instrument()
    {
    }

    Instrument(const casacore::String &name, const casacore::MPosition &position);

    template <typename T>
    Instrument(const casacore::String &name, const casacore::MPosition &position,
               T first, T last);

    const casacore::String &name() const;
    const casacore::MPosition &position() const;

    uint nStations() const;
    const Station &station(uint i) const;
    const Station &station(const casacore::String &name) const;

    void append(const Station &station);

  private:
    casacore::String              m_name;
    casacore::MPosition           m_position;
    map<casacore::String, uint>   m_index;
    vector<Station>           m_stations;
  };

  inline uint AntennaField::nTileElement() const
  {
    return m_tileElements.size();
  }

  const Vector3 &AntennaField::tileElement(uint i) const
  {
    return m_tileElements[i];
  }

  inline uint AntennaField::nElement() const
  {
    return m_elements.size();
  }

  inline const AntennaField::Element &AntennaField::element(uint i) const
  {
    return m_elements[i];
  }

  template <typename T>
  Instrument::Instrument(const casacore::String &name,
                         const casacore::MPosition &position,
                         T first, T last)
    :   m_name(name),
        m_position(position),
        m_stations(first, last)
  {
  }

  class BeamCoeff
  {
  public:
    BeamCoeff();

    void load(const casacore::Path &path);

    // Center frequency used to scale frequency to range [-1.0, 1.0].
    double center() const
    {
      return m_center;
    }

    // Width used to scale frequency to range [-1.0, 1.0].
    double width() const
    {
      return m_width;
    }

    uint nElements() const
    {
      return m_coeff.shape()(0);
    }

    uint nPowerFreq() const
    {
      return m_coeff.shape()(1);
    }

    uint nPowerTheta() const
    {
      return m_coeff.shape()(2);
    }

    uint nHarmonics() const
    {
      return m_coeff.shape()(3);
    }

    casacore::DComplex operator()(uint i, uint freq, uint theta, uint harmonic) const
    {
      return m_coeff(casacore::IPosition(4, i, freq, theta, harmonic));
    }

  private:
    double                      m_center, m_width;
    casacore::Array<casacore::DComplex> m_coeff;
  };

  class LofarATermOld
  {
  public:
    LofarATermOld(const casacore::MeasurementSet &ms,
               const casacore::String &beamElementPath);

    vector<casacore::Cube<casacore::Complex> > evaluate(const casacore::IPosition &shape,
      const casacore::DirectionCoordinate &coordinates,
      uint station,
      const casacore::MEpoch &epoch,
      const casacore::Vector<casacore::Double> &freq,
      bool normalize = false) const;

  private:
    casacore::Array<casacore::DComplex>
    normalize(const casacore::Array<casacore::DComplex> &response) const;

    casacore::Cube<casacore::Double>
    computeITRFMap(const casacore::DirectionCoordinate &coordinates,
      const casacore::IPosition &shape,
      casacore::MDirection::Convert convertor) const;

    casacore::Array<casacore::DComplex> evaluateStationBeam(const Station &station,
      const Vector3 &refDelay,
      const Vector3 &refTile,
      const casacore::Cube<casacore::Double> &map,
      const casacore::Vector<casacore::Double> &freq) const;

    casacore::Cube<casacore::DComplex> evaluateTileArrayFactor(const AntennaField &field,
      const Vector3 &reference,
      const casacore::Cube<casacore::Double> &map,
      const casacore::Vector<casacore::Double> &freq) const;

    casacore::Array<casacore::DComplex> evaluateElementBeam(const BeamCoeff &coeff,
      const AntennaField &field,
      const casacore::Cube<casacore::Double> &map,
      const casacore::Vector<casacore::Double> &freq) const;

    void initInstrument(const casacore::MeasurementSet &ms);

    Station initStation(const casacore::MeasurementSet &ms,
      uint id,
      const casacore::String &name,
      const casacore::MPosition &position) const;

    void initReferenceDirections(const casacore::MeasurementSet &ms, uint idField);

    void initReferenceFreq(const casacore::MeasurementSet &ms,
      uint idDataDescription);

    BeamCoeff        m_coeffLBA, m_coeffHBA;
    casacore::MDirection m_refDelay, m_refTile;
    double           m_refFreq;
    Instrument       m_instrument;
  };
} // namespace LOFAR

#endif
