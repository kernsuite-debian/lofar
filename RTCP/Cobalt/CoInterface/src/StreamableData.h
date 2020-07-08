//# StreamableData.h
//# Copyright (C) 2008-2013, 2017
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
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

#ifndef LOFAR_INTERFACE_STREAMABLE_DATA_H
#define LOFAR_INTERFACE_STREAMABLE_DATA_H

#include <cstring>

#include <Common/LofarTypes.h>
#include <Common/DataConvert.h>
#include <Stream/Stream.h>
#include "Parset.h"
#include "MultiDimArray.h"
#include "SparseSet.h"
#include "Allocator.h"
#include "RSP.h"

namespace LOFAR
{
  namespace Cobalt
  {

    // TODO: Update documentation.
    // Data which needs to be transported between CN, ION and Storage.
    // Apart from read() and write() functionality, the data is augmented
    // with a sequence number in order to detect missing data. Furthermore,
    // an integration operator += can be defined to reduce the data.
    class StreamableData
    {
    public:
      static const uint32_t magic = 0xda7a;
      static const size_t alignment = 512;

      // the CPU which fills the datastructure sets the peerMagicNumber,
      // because other CPUs will overwrite it with a read(s,true) call from
      // either disk or network.
      StreamableData(bool readWithSeqNr = true, bool writeWithSeqNr = true)
      : peerMagicNumber(magic),
        readWithSequenceNumber(readWithSeqNr),
        writeWithSequenceNumber(writeWithSeqNr),
        rawSequenceNumber(0)
      {
      }

      virtual ~StreamableData()
      {
      }

      void read(Stream *, unsigned align);
      void write(Stream *, unsigned align);

      bool shouldByteSwap() const
      {
        return peerMagicNumber != magic;
      }

      uint32_t sequenceNumber(bool raw = false) const
      {
        if (shouldByteSwap() && !raw) {
          uint32_t seqno = rawSequenceNumber;

          byteSwap32(&seqno);

          return seqno;
        } else {
          return rawSequenceNumber;
        }
      }

      void setSequenceNumber(uint32_t seqno)
      {
        if (shouldByteSwap())
          byteSwap32(&seqno);

        rawSequenceNumber = seqno;
      }

      bool doReadWithSequenceNumber()
      {
        return readWithSequenceNumber;
      }

      virtual void setDimensions(unsigned, unsigned, unsigned)
      {
      }

      // Fraction of data that was lost due to output bottlenecks
      virtual double outputLossFraction() const
      {
        return 0.0;
      }

      uint32_t peerMagicNumber;  /// magic number received from peer

    protected:
      // a subclass should override these to marshall its data
      virtual void readData(Stream *, unsigned) = 0;
      virtual void writeData(Stream *, unsigned) = 0;

    private:
      bool readWithSequenceNumber;
      bool writeWithSequenceNumber;
      uint32_t rawSequenceNumber; /// possibly needs byte swapping
    };


    // A typical data set contains a MultiDimArray of tuples and a set of flags.
    template <typename T = fcomplex, unsigned DIM = 4, unsigned FLAGS_DIM = 2>
    class SampleData : public StreamableData
    {
    public:
      typedef typename MultiDimArray<T,DIM>::ExtentList ExtentList;
      typedef typename MultiDimArray<SparseSet<unsigned>,FLAGS_DIM>::ExtentList FlagsExtentList;

      SampleData(const ExtentList &extents, const FlagsExtentList &flagsExtents, Allocator & = heapAllocator);

      MultiDimArray<T,DIM>              samples;
      MultiDimArray<SparseSet<unsigned>,FLAGS_DIM>   flags;

    protected:
      virtual void readData(Stream *, unsigned);
      virtual void writeData(Stream *, unsigned);
    };


    inline void StreamableData::read(Stream *str, unsigned alignment)
    {
      if (readWithSequenceNumber) {
        std::vector<char> header(alignment > 2 * sizeof(uint32_t) ? alignment : 2 * sizeof(uint32_t));
        uint32_t          &magicValue = *reinterpret_cast<uint32_t *>(&header[0]);
        uint32_t          &seqNo = *reinterpret_cast<uint32_t *>(&header[sizeof(uint32_t)]);

        str->read(&header[0], header.size());

        peerMagicNumber = magicValue;
        rawSequenceNumber = seqNo;
      }

      readData(str, alignment);
    }


    inline void StreamableData::write(Stream *str, unsigned alignment)
    {

      if (writeWithSequenceNumber) {
        /*     std::vector<char> header(alignment > sizeof(uint32_t) ? alignment : sizeof(uint32_t)); */
        std::vector<char> header(alignment > 2 * sizeof(uint32_t) ? alignment : 2 * sizeof(uint32_t));
        uint32_t          &magicValue = *reinterpret_cast<uint32_t *>(&header[0]);
        uint32_t          &seqNo = *reinterpret_cast<uint32_t *>(&header[sizeof(uint32_t)]);

#if defined USE_VALGRIND
        std::memset(&header[0], 0, header.size());
#endif

        magicValue = peerMagicNumber;
        seqNo = rawSequenceNumber;

        str->write(&header[0], header.size());
      }

      writeData(str, alignment);
    }


    template <typename T, unsigned DIM, unsigned FLAGS_DIM>
    inline SampleData<T,DIM,FLAGS_DIM>::SampleData(const ExtentList &extents, const FlagsExtentList &flagsExtents, Allocator &allocator)
      :
      // This clarifies seq nr handling for beamforming, however, beamformed output is *not*
      // written via StreamableData->write(), but in a custom way in MSWriterDAL::write().
      StreamableData(true, false),
      samples(extents, alignment, allocator),
      flags(flagsExtents) // e.g., for FilteredData [nrChannels][nrStations], sparse dimension [nrSamplesPerIntegration]
    {
    }


    template <typename T, unsigned DIM, unsigned FLAGS_DIM>
    inline void SampleData<T,DIM,FLAGS_DIM>::readData(Stream *str, unsigned alignment)
    {
      (void)alignment;

      str->read(samples.origin(), samples.num_elements() * sizeof(T));
    }


    template <typename T, unsigned DIM, unsigned FLAGS_DIM>
    inline void SampleData<T,DIM,FLAGS_DIM>::writeData(Stream *str, unsigned alignment)
    {
      (void)alignment;

      str->write(samples.origin(), samples.num_elements() * sizeof(T));
    }


    class RSPRawData : public StreamableData
    {
    public:
      RSPRawData()
      : StreamableData(false, false), // raw: no seq nrs
        buffer(bufferSize),
        used(0)
      {
      }

    protected:
      virtual void readData(Stream *str, unsigned alignment)
      {
        (void)alignment;

        used = str->tryRead(&buffer[0], bufferSize); // don't know what to expect, so read what is avail
      }

      virtual void writeData(Stream *str, unsigned alignment)
      {
        (void)alignment;

        str->write(&buffer[0], used);
        used = 0;
      }

    private:
      static const unsigned bufferSize = 64 * sizeof(RSP);

      vector<uint8_t> buffer; // vector<RSP> could have worked, but byte stream from TCP to storage
      size_t used;
    };

  } // namespace Cobalt
} // namespace LOFAR

#endif
