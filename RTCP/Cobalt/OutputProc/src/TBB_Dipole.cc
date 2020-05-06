//# TBB_Dipole.cc: TBB per-dipole routines to store incoming TBB data
//# Copyright (C) 2012-2017  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include "TBB_Dipole.h"

#include <exception>
#include <sstream>
#include <cstring>
#include <unistd.h>
#include <endian.h>
#if __BYTE_ORDER != __BIG_ENDIAN && __BYTE_ORDER != __LITTLE_ENDIAN
#error Byte order is neither big endian nor little endian: not supported
#endif
#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>

#ifdef basename // some glibc have this as a macro
#undef basename
#endif
#include <Common/SystemUtil.h>
#include <Common/LofarLogger.h>
#include <Common/SystemCallException.h>

namespace LOFAR
{
  namespace Cobalt
  {

    using namespace std;

    // LCS/Stream FileStream does not wrap pwrite(2). No other LOFAR source uses it, so define it here in the same way.
    static size_t tryPWrite(int fd, const void *ptr, size_t size, off64_t offset)
    {
      ssize_t bytes = ::pwrite(fd, ptr, size, offset);
      if (bytes < 0)
        THROW_SYSCALL("pwrite");
      return bytes;
    }

    static void pwrite(int fd, const void *ptr, size_t size, off64_t offset)
    {
    LOG_DEBUG_STR("TBB pwrite fd=" << fd << \
                " ptr=" << ptr << \
                " size=" << size << \
                " offset=" << offset);

      while (true) {
        size_t bytes = tryPWrite(fd, ptr, size, offset);
        size -= bytes;
        if (size == 0) {
          return;
        }
        offset += bytes;
        ptr = static_cast<const char *>(ptr) + bytes;
      }
    }



    static std::string getRawFilename(const std::string& h5Filename,
        uint32_t rspID, uint32_t rcuID)
    {
        std:: string rawFilename{h5Filename};
        std::string rspRcuSbStr{boost::str(
            boost::format("_RSP%03u_RCU%03u") % rspID % rcuID)};

        const std::size_t pos{rawFilename.find('_', rawFilename.find('_') + 1)};

        // insert _RSPxxx_RCUxxx after station name (2nd '_')
        rawFilename.insert(pos, rspRcuSbStr);
        rawFilename.resize(rawFilename.size() - (sizeof(".h5") - 1));
        rawFilename.append(".raw");

        return rawFilename;
    }

    uint32_t getTransientModeSampleNr(const TBB_Header& header)
    {
      /*
       * In transient mode, at 200 MHz we get DEFAULT_TBB_TRANSIENT_NSAMPLES (1024) samples per frame: 195312.5 frames/s.
       * This means that every 2 seconds, a frame overlaps a seconds boundary. But the sample values generated
       * by the RSPs start at zero for each second, even if it should start at 512 for odd timestamps at 200 MHz.
       * At 160 MHz sample rate, an integer number of frames fits in a second (156250), so no correction is needed.
       */
      uint32_t sampleNr = header.sampleNr;
      if (header.sampleFreq == 200 && (header.time & 1)) {
        sampleNr += DEFAULT_TBB_TRANSIENT_NSAMPLES / 2;
      }
      return sampleNr;
    }

    uint32_t getSpectralModeBandNr(const TBB_Header& header)
    {
        return (header.bandSliceNr & TBB_BAND_NR_MASK);
    }

    uint32_t getSpectralModeSliceNr(const TBB_Header& header)
    {
        return (header.bandSliceNr >> TBB_SLICE_NR_SHIFT);
    }

    bool hasAllZeroDataSamples(const TBB_Payload& payload,
        std::size_t numberOfSamples)
    {
        /**
         * Good (noisy) data may have a few consecutive zero values, so this loop
         * terminates quickly, unless the antenna is broken or disabled, which
         * happens sometimes.
         * Another reason for all zeros is that a wave generator is used and set
         * to zero amp (pointless).
         *
         * Unfortunately, the crc32 variant used does not reject all zeros because
         * the checksum would be 0.
         */
        for(std::size_t index{0U}; index < numberOfSamples; ++index)
        {
            if(payload.data[index] != 0)
            {
                return false;
            }
        }

        return true;
    }


    TBB_Dipole::TBB_Dipole():
        itsDALDipole(),
        itsLastLogErrorTime(0),
        tbbMode{TBB_MODE_TRANSIENT}
    {
    }

    // Do not use. Only needed for vector<TBB_Dipole>(N).
    TBB_Dipole::TBB_Dipole(const TBB_Dipole& rhs):
        itsDALDipole(),
        itsLastLogErrorTime(rhs.itsLastLogErrorTime),
        tbbMode{rhs.tbbMode}
    {
    }

    TBB_Dipole::~TBB_Dipole()
    {
        /**
         * Executed by the main thread after joined with all workers, so no
         * need to lock or delay cancellation.
         */
        if(isInitialized())
        {
            const bool transientMode(doTransient());
            try
            {
                if(transientMode == true)
                {
                    itsDipoleDataset()->resize1D(itsDumpInfo.itsDatasetLen);
                }
            }
            catch(exception& exc)
            {
                // dal::DALException, or std::bad_alloc from vector constr
                LOG_WARN_STR("TBB: failed to resize HDF5 dipole dataset to "
                    "external data size: "
                    << exc.what());
            }

            try
            {
                // Thus in values (scalar for transient mode, complex for subband mode)
                if(transientMode == true)
                {
                    itsDipoleDataset()->dataLength().value =
                        itsDumpInfo.itsDatasetLen;
                }
            }
            catch(dal::DALException& exc)
            {
                LOG_WARN_STR("TBB: failed to set dipole DATA_LENGTH attribute: "
                    << exc.what());
            }
            try
            {
                /**
                 * We write flags at the end, because HDF5 attributes can only
                 * be (re)set, not updated.
                 *
                 * TODO: If an .h5 internal (non-chunked!) 1D dataset would be
                 * possible without pre-specifying size, that would be better.
                 * Then we can write flags while data comes in. Else, leave
                 * as-is.
                 */
                if(transientMode == true)
                {
                    itsDipoleDataset()->flagOffsets().create(
                        itsDumpInfo.itsFlagOffsets.size()).set(
                            itsDumpInfo.itsFlagOffsets);
                }
            }
            catch(dal::DALException& exc)
            {
                LOG_WARN_STR("TBB: failed to set dipole FLAG_OFFSETS "
                    "attribute: "
                    << exc.what());
            }
        }
    }

    // Add a new flag range at the end or extend the last stored flag range. 'len' may not be 0.
    void TBB_Dipole::appendFlags(DumpInfo& di, uint64_t offset,
        std::size_t len)
    {
        if((di.itsFlagOffsets.empty() == true)
        || (offset > di.itsFlagOffsets.back().end))
        {
            di.itsFlagOffsets.push_back(dal::Range(offset, offset + len));
        }
        else
        {
            // extend
            di.itsFlagOffsets.back().end += len;
        }
    }

    void TBB_Dipole::init(const TBB_Header& header, const Parset& parset,
        const StationMetaData& stationMetaData,
        const std::map< uint32_t, double >& allSubbandCentralFreqs,
        const std::string& h5Filename,
        const std::size_t totalSubBandSizeInSamples, dal::TBB_Station& station,
        Mutex& h5Mutex)
    {
        itsH5Filename = h5Filename;
        itsAllSubbandCentralFreqs = allSubbandCentralFreqs;
        if(itsAllSubbandCentralFreqs.empty() == true)
        {
            tbbMode = TBB_MODE_TRANSIENT;
        }
        else
        {
            tbbMode = TBB_MODE_SPECTRAL;
        }

        if(doTransient() == true)
        {
            itsDumpInfo.itsDatasetLen = 0;
            itsDumpInfo.itsTime0 = header.time;
            itsDumpInfo.itsSampleNr0 = getTransientModeSampleNr(header);
        }
        else
        {
            // spectral mode
            const std::vector< uint32_t > subBandsToBeStored{
                parset.getUint32Vector(
                    "Observation.TBB.TBBsetting.subbandList", true)};

            std::ostringstream bands;
            for(const auto subBand: subBandsToBeStored)
            {
                subBandBookKeeping.insert(std::make_pair(subBand,
                    SubBandBookKeeping(subBand, totalSubBandSizeInSamples,
                        allSubbandCentralFreqs.at(subBand))));
                bands << (boost::format("%03u, ") % subBand);
            }
            LOG_INFO_STR("TBB:  Storing the following sub-bands: "
                << bands.str());
        }

        const std::string rawFilename{getRawFilename(h5Filename,
            header.rspID, header.rcuID)};
        {
            ScopedLock h5OutLock(h5Mutex);
            initTBB_DipoleGroupOrDataset(header, parset, stationMetaData,
                rawFilename, station);
        }
    }

    bool TBB_Dipole::isInitialized() const
    {
        return !!itsDALDipole;
    }

    bool TBB_Dipole::doTransient() const
    {
        return (tbbMode == TBB_MODE_TRANSIENT);
    }

    void TBB_Dipole::processTransientFrameData(const TBB_Frame& frame)
    {
      /*
       * Out-of-order frame arrival has not been seen for Dutch stations. TBB from int'l stations is not (yet) dumped to CEP.
       * We could support out-of-order arrival, except for packets that appear to be overtaken by the 1st packet received,
       * but this makes flagging lost packets more complicated than how we deal with it using appendFlags() below.
       * Also, fake out-of-order occurs when data is dumped (incorrectly) across the frozen TBB write pointer (LOFAR control bug).
       */
      uint32_t sampleNr = getTransientModeSampleNr(frame.header);
      if (frame.header.time < itsDumpInfo.itsTime0 ||
          (frame.header.time == itsDumpInfo.itsTime0 && sampleNr < itsDumpInfo.itsSampleNr0)) {
        logErrorRateLimited(&itsLastLogErrorTime, "TBB: unhandled out-of-order packet: " +
                                                  frame.header.to_string());
        return;
      }

      uint64_t offset = (frame.header.time - itsDumpInfo.itsTime0) * frame.header.sampleFreq * 1000000;
      offset += sampleNr - itsDumpInfo.itsSampleNr0;

      /*
       * Flag lost frame(s) (assume no out-of-order).
       * Assumes all frames (except maybe the last) have the same nr of samples.
       * This cannot detect lost frames at the end of a dataset.
       */
      int64_t nskipped = offset - itsDumpInfo.itsDatasetLen; // should be > 0, but do signed cmp to avoid crazy flagging range
      if (nskipped > 0) {
        appendFlags(itsDumpInfo, itsDumpInfo.itsDatasetLen, (uint64_t)nskipped);
      }

      // On a data checksum error or all zeros, flag these samples.
      if (!crc32tbb(&frame.payload, frame.header.nOfSamplesPerFrame)) {
        appendFlags(itsDumpInfo, offset, frame.header.nOfSamplesPerFrame);
        uint32_t crc32;
        memcpy(&crc32, &frame.payload.data[frame.header.nOfSamplesPerFrame], sizeof crc32); // strict-aliasing safe
        logErrorRateLimited(&itsLastLogErrorTime, "TBB: crc32 error: " + frame.header.to_string() +
                                                  " crc32: " + boost::lexical_cast<string>(crc32));
      } else if (hasAllZeroDataSamples(frame.payload, frame.header.nOfSamplesPerFrame)) {
        appendFlags(itsDumpInfo, offset, frame.header.nOfSamplesPerFrame);
      }

      // Since we are writing around HDF5, there is no need to lock. Resize the HDF5 dataset in the destructor.
      pwrite(itsDumpInfo.itsRawFile->fd, frame.payload.data, frame.header.nOfSamplesPerFrame * sizeof(int16_t),
             static_cast< off64_t >(offset * sizeof(int16_t)));
      itsDumpInfo.itsDatasetLen = offset + frame.header.nOfSamplesPerFrame;
    }

    void TBB_Dipole::processSpectralFrameData(const TBB_Frame& frame)
    {
        /**
         * NOTE:
         * only intends to support TBB-ALERT subband mode, and normal subband
         * mode with 1 band per packet!
         */

        /**
         * NOTE:
         * frame header bandSel may have multiple bits set.
         * Atm, we don't support this, because the (other) bandNr sub-field in
         * the header appears odd wrt the spec (e.g. 0 even if band 0 is not
         * dumped (maybe it's an index?)) for multi-subband dumps.
         * The TBB-ALERT subband mode firmware does not send (parts of) multiple
         * subbands per packet anyway.
         */
        const unsigned int bandSelNr{frame.header.getFirstBandSelNr()};
        if(bandSelNr == RSP_NR_SUBBANDS)
        {
            logErrorRateLimited(&itsLastLogErrorTime,
                "TBB: dropping packet: "
                    "subband mode, but empty bandSel bitmap in packet header");
            return;
        }

        const uint32_t bandNr{getSpectralModeBandNr(frame.header)};
        const uint32_t sliceNr{getSpectralModeSliceNr(frame.header)};

        const auto incomingSubBand{subBandBookKeeping.find(bandNr)};
        if(incomingSubBand == subBandBookKeeping.end())
        {
            LOG_WARN_STR("TBB: Received a frame for sub-band #"
               << bandNr
               << " but that sub-band is unexpected!  Ignoring it.");
            return;
        }

        struct SubBandBookKeeping& currentSubBand{incomingSubBand->second};
        /**
         * Do I need to store this sub-band or was it already complete?
         */
        if(currentSubBand.isComplete == true)
        {
            LOG_WARN_STR("TBB: Received a frame for sub-band #"
               << bandNr
               << " but more data for this sub-band is unexpected.  It "
                   "appears that the data is already complete.  Ignoring "
                   "this frame.");
            return;
        }
        /**
         * Lazily initialize last part of the book keeping map from the 1st
         * frame that is received for a sub-band.
         * subBandBookKeeping[bandNr].isInitialised is set to false when
         * TBB_Dipole::init gets called and sets up the book keeping map.
         *
         * Also create a new TBB_SubbandDataset in the DipoleGroup
         */
        else if(currentSubBand.isInitialised == false)
        {
            /**
             * Assume that the first ever received frame for any sub-band is
             * the very first frame that got ever sent for that sub-band.  This
             * is the only assumption made about the order of frames sent by
             * TBB.
             */
            currentSubBand.time0 = frame.header.time;
            currentSubBand.slice0 = sliceNr;

            currentSubBand.dataSet.reset(new dal::TBB_SubbandDataset(
                itsDipoleGroup()->subband(bandNr)));
            // Store the data in the hdf5 file.  Do not provide a file name!
            try
            {
                currentSubBand.dataSet->create1D(
                    currentSubBand.totalSubBandSizeInSamples,
                    currentSubBand.totalSubBandSizeInSamples,
                    "",
                    currentSubBand.dataSet->LITTLE);
            }
            catch(std::exception& ex)
            {
                LOG_ERROR_STR("TBB: Caught a DAL exception when trying to "
                    "create the HDF5 data set for sub-band #"
                    << bandNr
                    << ":  \""
                    << ex.what()
                    << "\"  To avoid further problems with this frame, the "
                        "frame's data will not be stored and the frame will "
                        "be discarded.");
                return;
            }

            currentSubBand.dataSet->groupType().value = "SubbandDataset";

            currentSubBand.dataSet->time().value = currentSubBand.time0;

            currentSubBand.dataSet->bandNumber().value = bandNr;
            currentSubBand.dataSet->sliceNumber().value = sliceNr;
            currentSubBand.dataSet->centralFrequency().value =
                currentSubBand.centralFrequency * 1e6;
            currentSubBand.dataSet->centralFrequencyUnit().value = "Hz";
            currentSubBand.dataSet->timeResolution().value =
                static_cast< double >(SPECTRAL_TRANSFORM_SIZE) /
                    (frame.header.sampleFreq * 1000000.0);
            currentSubBand.dataSet->timeResolutionUnit().value = "s";
            currentSubBand.dataSet->bandwidth().value =
                static_cast< double >(frame.header.sampleFreq) * 1000000.0 /
                    static_cast< double >(SPECTRAL_TRANSFORM_SIZE);
            currentSubBand.dataSet->bandwidthUnit().value = "Hz";

            // Filled in when the sub-band is complete:
            currentSubBand.dataSet->dataLength().value = 0;
            /**
             * ATTENTION!
             * Storing this value makes no sense.  Only if all frames of a
             * sub-band contain the same number of samples then this value
             * is representing something real.
             * But obviously this is only true if all n frames of a
             * sub-band, 0 < n < infinity, contain exactly the same number
             * of samples.
             *
             * A simple example that is pretty general where this does not
             * hold:
             * - Every sub-band that has a last frame with less than 480
             *   samples would have two values:  480 and the number of
             *   samples in the last frame.
             */
            currentSubBand.dataSet->samplesPerFrame().value =
                frame.header.nOfSamplesPerFrame;

            currentSubBand.isInitialised = true;

            LOG_INFO_STR("TBB:  Sub-band #"
                << currentSubBand.bandNr
                << " initialised with the following data:  time0 = "
                << currentSubBand.time0
                << ", slice0 = "
                << currentSubBand.slice0
                << ", HDF5 SubbandDataset name = "
                << currentSubBand.dataSet->name()
                << ", dipole = "
                << itsDipoleGroup()->name()
                << ", station id = "
                << static_cast< uint32_t >(frame.header.stationID)
                << ", rsp = "
                << static_cast< uint32_t >(frame.header.rspID)
                << ", rcu = "
                << static_cast< uint32_t >(frame.header.rcuID));
        }

        /**
         * Out-of-order frame arrival has not been seen for Dutch stations.
         * TBB from int'l stations is not (yet) dumped to CEP.
         *
         * But:
         *
         * We support out-of-order arrival, except for packets that appear to
         * have been overtaken by the 1st packet received.  But this makes
         * flagging lost packets more complicated than how we deal with it
         * using appendFlags() below.
         *
         * Also, fake out-of-order occurs when data is dumped (incorrectly)
         * across the frozen TBB write pointer (LOFAR control bug).
         */
        if((frame.header.time < currentSubBand.time0)
        || ((frame.header.time == currentSubBand.time0)
            && (sliceNr < currentSubBand.slice0)))
        {
            logErrorRateLimited(&itsLastLogErrorTime, "TBB: received an "
                "out-of-order packet!  Current start time of first frame for "
                "this data stream: "
                + boost::lexical_cast< std::string >(currentSubBand.time0)
                + ", current sample or slice nr of the first frame for this "
                "data stream:  "
                + boost::lexical_cast< std::string >(currentSubBand.slice0)
                + ", received frame header:  "
                + frame.header.to_string());
            return;
        }

        /**
         * With a 200 MHz sample freq, even seconds have one extra slice (that
         * actually falls half-way).
         *
         * Calculate the offset of the frame start from the time stamp of the
         * first received frame.  Use 64 bit integers so that negative numbers
         * can be handled.
         */
        int64_t offset{frame.header.time};
        offset -= currentSubBand.time0;
        LOG_DEBUG_STR("TBB: offset = frame.header.time - currentSubBand.time0, "
            << offset << ", "
            << frame.header.time << ", "
            << currentSubBand.time0);

        /**
         * Convert the offset in [s] to the total number of samples (containing
         * a complex number of two 16 bit integers).  sampleFreq is in MHz.
         */
        offset *= (frame.header.sampleFreq * 1000000);
        LOG_DEBUG_STR("TBB: offset *= (frame.header.sampleFreq * 1000000), "
          << offset << ", "
          << static_cast< uint32_t >(frame.header.sampleFreq));

        /**
         * Divide the offset, i.e. the number of samples by the size of an FFT
         * block.  The result is the index of the raw voltage sampling window
         * (size 1024 values) that got fed into the FFT.  This not a sample
         * within the window but just a rough indicator which window we are in!
         * [   1024   ][   1024   ][   1024   ]
         *         ^
         *         |  Start recording
         *  ^
         *  | Window number of the 0th TBB data frame
         *                         ^
         *                         |  Window number of frame N
         * This is also then the index of the TBB frame for this frequency
         * because the begin of a voltage window is also the begin of a
         * frequency window.
         */
        offset /= SPECTRAL_TRANSFORM_SIZE;
        LOG_DEBUG_STR("TBB: offset /= SPECTRAL_TRANSFORM_SIZE, "
            << offset
            << ", "
            << SPECTRAL_TRANSFORM_SIZE);

        /**
         * Now try to figure out where in the raw voltage data window our
         * spectral frame exactly begins.
         * Add that then to the offset.
         *
         * Attention!
         * Both slice numbers were already divided by SPECTRAL_TRANSFORM_SIZE!
         */
        offset += sliceNr;
        offset -= currentSubBand.slice0;
        LOG_DEBUG_STR("TBB: offset += sliceNr - currentSubBand.slice0, "
          << offset << ", "
          << sliceNr << ", "
          << currentSubBand.slice0);

        /**
         * Now check for even/odd seconds.  Why?  Because
         * sampling frequency / (N * 1024) does not result in an integer without
         * rest.  So one 1024 slice has to be moved to either ever odd or to
         * every even second:
         *
         * slice #195312        slice #195313          slice #0
         *      |                     |                    |
         *      v                     v                    v
         * 1024 ---------|--------- 1024 --------- |--------- 1024
         *                            ^
         *                            |
         *              A new odd second begins here.
         *
         * slice #195312        slice #0               slice #1
         *      |                     |                    |
         *      v                     v                    v
         * 1024 ---------|--------- 1024 --------- |--------- 1024
         *               ^
         *               |
         *  A new even second begins here.
         *
         * What does this all mean?
         * ------------------------
         * If the time-stamp of the second of the first frame is even then
         * the last frame had slice numbers up to #195313.
         * The following slice numbers for the next second will only go up to
         * #195312.
         * - Check if the frame #0's second is even, then
         * - check if the second of the current frame is odd.
         * - Both yes:  means that we have to add one sample to the offset.
         */
        if((currentSubBand.time0 % 2 == 0) && (frame.header.time % 2 == 1))
        {
            offset += 1;
            LOG_DEBUG_STR("TBB:  Added one sample to the offset because t0 is "
                "even and t_now is odd:  currentSubBand.time0 = "
                << currentSubBand.time0
                << ", frame.header.time = "
                << frame.header.time
                << ", offset = "
                << offset);
        }

        /**
         * On a data checksum error or all zeros, flag these samples.
         * TBB Design Doc states the crc32 is computed for transient data only,
         * but the firmware developer (Wietse Poiesz) says it is also valid for
         * spectral data.
         * But in data dumps I've seen, it looked invalid for the first
         * spectral frame each second; recheck this (?).
         */
        if(0)
        {
            // !crc32tbb(frame.payload.data, 2 * frame.header.nOfSamplesPerFrame)) {
            // in (complex) values
            appendFlags(itsDumpInfo, offset, frame.header.nOfSamplesPerFrame);
            uint32_t crc32{0U};
            // strict-aliasing safe
            std::memcpy(&crc32,
                &frame.payload.data[2 * frame.header.nOfSamplesPerFrame],
                sizeof(uint32_t));
            logErrorRateLimited(&itsLastLogErrorTime, "TBB: crc32 error: "
                + frame.header.to_string()
                + " crc32: " + boost::lexical_cast<string>(crc32));
        }

        LOG_DEBUG_STR("TBB: offset in samples calculated for the HDF5 data set "
            "= "
            << offset
            << " for sub-band #"
            << bandNr);

        /**
         * Now check if the number of samples in the frame plus the number of
         * samples in the HDF5 array that we have stored so far exceeds the
         * expected number of samples.  If so, then just store up to the number
         * of expected samples and discard the rest.
         */
        std::size_t numberOfSamplesToBeStored{frame.header.nOfSamplesPerFrame};
        if((numberOfSamplesToBeStored + currentSubBand.currentSizeInSamples)
            > currentSubBand.totalSubBandSizeInSamples)
        {
            numberOfSamplesToBeStored = currentSubBand.totalSubBandSizeInSamples
                - currentSubBand.currentSizeInSamples;
            LOG_WARN_STR("TBB: Received too many samples for sub-band #"
                << bandNr
                << ".  "
                << (frame.header.nOfSamplesPerFrame - numberOfSamplesToBeStored)
                << " samples will be discarded!");
        }

        /**
         * I know, I know.  These two casts are not good.  I tried to use a
         * union for a std::complex< int16_t > type but C++ would not let me.
         * Next best thing is a union of int16_t[] and int16_t[][2]. And hence
         * the weird casting.
         */
        try
        {
            currentSubBand.dataSet->set1D(offset,
                reinterpret_cast< std::complex< int16_t > * >(
                    const_cast< int16_t * >(&(frame.payload.spectralData[0][0]))),
                numberOfSamplesToBeStored, 0);
        }
        catch(std::exception& ex)
        {
            LOG_WARN_STR("TBB:  Caught a DAL exception when storing data for "
                "sub-band #"
                << bandNr
                << ":  \""
                << ex.what()
                << "\"  To avoid further problems with this frame, the frame's "
                    "data will not be stored and the frame will be discarded.");
            return;
        }

        // in (complex) values
        currentSubBand.currentSizeInSamples += numberOfSamplesToBeStored;

        /**
         * Check if the currently handled sub-band has received enough samples
         * (subbandSizeInSamples).  If so, then remove the currently handled
         * sub-band from remainingSubbandsToBeStored
         */
        if(currentSubBand.currentSizeInSamples >=
            currentSubBand.totalSubBandSizeInSamples)
        {
            currentSubBand.dataSet->dataLength().value =
                currentSubBand.currentSizeInSamples;
            currentSubBand.dataSet->flagOffsets().create(
                itsDumpInfo.itsFlagOffsets.size()).set(
                    itsDumpInfo.itsFlagOffsets);
            currentSubBand.isComplete = true;

            LOG_INFO_STR("TBB: Data for sub-band #"
                << bandNr
                << ", dipole = "
                << itsDipoleGroup()->name()
                << ", rcu = "
                << static_cast< uint32_t >(frame.header.rcuID)
                << " is now complete has been stored in the HDF5 file.");

            bool allComplete{true};
            for(auto& subBand: subBandBookKeeping)
            {
                allComplete &= subBand.second.isComplete;
            }

            if(allComplete == true)
            {
                LOG_INFO_STR("TBB: Sub-band data for dipole "
                    << itsDipoleGroup()->name()
                    << ", station id = "
                    << static_cast< uint32_t >(frame.header.stationID)
                    << ", rsp = "
                    << static_cast< uint32_t >(frame.header.rspID)
                    << ", rcu = "
                    << static_cast< uint32_t >(frame.header.rcuID)
                    << " should now be complete in the HDF5 file.");
            }
        }
    }

        void TBB_Dipole::initTBB_DipoleGroupOrDataset(const TBB_Header& header,
            const Parset& parset, const StationMetaData& stationMetaData,
            const string& rawFilename, dal::TBB_Station& station)
        {
            const bool transientMode{doTransient()};

            // Override endianess. TBB data is always stored little endian and also received as such, so written as-is on any platform.
            if(transientMode == true)
            {
                const string filename = LOFAR::basename(rawFilename); // don't store paths in HDF5
                itsDALDipole.reset(new dal::TBB_DipoleDataset(
                        station.dipoleDataset(header.stationID, header.rspID,
                            header.rcuID)));
                dal::TBB_DipoleDataset* dipoleDataSet{itsDipoleDataset()};
                dipoleDataSet->create1D(0, -1, filename, dipoleDataSet->LITTLE);
                dipoleDataSet->groupType().value = "DipoleDataset";

                dipoleDataSet->sampleNumber().value = getTransientModeSampleNr(
                    header);
                dipoleDataSet->time().value = header.time; // in seconds
                dipoleDataSet->samplesPerFrame().value = header
                    .nOfSamplesPerFrame; // possibly sanitized

                //dipoleDataSet->dataLength().value is set at the end (destr)
                //dipoleDataSet->flagOffsets().value is set at the end (destr)
            }
            else
            {
                // spectral mode
                itsDALDipole.reset(
                    new dal::TBB_DipoleGroup(station.dipoleGroup(
                        header.stationID, header.rspID, header.rcuID)));
                dal::TBB_DipoleGroup* dipoleGroup{itsDipoleGroup()};
                dipoleGroup->create();
                dipoleGroup->groupType().value = "DipoleGroup";

                //TODO 20181127 initialize these from somewhere
                dipoleGroup->adc2voltage();
                dipoleGroup->dispersionMeasure();
                dipoleGroup->dispersionMeasureUnit();
                const std::vector< uint32_t > subBandsToBeStored{
                    parset.getUint32Vector(
                        "Observation.TBB.TBBsetting.subbandList", true)};
                dipoleGroup->nofSubbands().value = subBandsToBeStored.size();
                dipoleGroup->subbands().value = subBandsToBeStored;
            }


            LOG_INFO_STR("TBB: Created HDF5 Dipole"
                << (transientMode == true ? "Dataset " : "Group ")
                << (transientMode == true ?
                        itsDipoleDataset()->name() : itsDipoleGroup()->name())
                << " for station "
                << station.stationName().value
                << ", stationID = "
                << static_cast< uint32_t >(header.stationID)
                << ", rsp = "
                << static_cast< uint32_t >(header.rspID)
                << ", rcu = "
                << static_cast< uint32_t >(header.rcuID));

            //set common properties for itsDALDipole, regardless whether it is a dal::TBB_DipoleDataset or a dal::TBB_DipoleGroup
            itsDALDipole->stationID().value = header.stationID;
            itsDALDipole->rspID().value = header.rspID;
            itsDALDipole->rcuID().value = header.rcuID;

            itsDALDipole->sampleFrequency().value = header.sampleFreq;
            itsDALDipole->sampleFrequencyUnit().value = "MHz";

            itsDALDipole->nyquistZone().value = parset.settings.nyquistZone();

            // Skip if station is not participating in the observation (should not happen).
            if(stationMetaData.available
                && 2u * 3u * header.rcuID + 2u
                    < stationMetaData.antPositions.size())
            { // bounds check for antPositions[]
                /*TODO
                 * Selecting the right positions depends on the antenna set. Checking vs the tables in
                 * lhn001:/home/veen/lus/src/code/data/lofar/antennapositions/ can help, but their repos may be outdated.
                 */
                vector< double > antPos(3);
                antPos[0] =
                    stationMetaData.antPositions[2u * 3u * header.rcuID];
                antPos[1] = stationMetaData.antPositions[2u * 3u * header.rcuID
                    + 1u];
                antPos[2] = stationMetaData.antPositions[2u * 3u * header.rcuID
                    + 2u];
                itsDALDipole->antennaPosition().create(antPos.size()).set(
                    antPos); // absolute position
                itsDALDipole->antennaPositionUnit().value = "m";
                itsDALDipole->antennaPositionFrame().value =
                    parset.positionType(); // "ITRF"

                /*
                 * The normal vector and rotation matrix are actually per antenna field,
                 * but given the HBA0/HBA1 "ears" depending on antenna set, it was
                 * decided to store them per antenna.
                 */
                itsDALDipole->antennaNormalVector().create(
                    stationMetaData.normalVector.size()).set(
                    stationMetaData.normalVector); // 3 doubles
                itsDALDipole->antennaRotationMatrix().create(
                    stationMetaData.rotationMatrix.size()).set(
                    stationMetaData.rotationMatrix); // 9 doubles, 3x3, row-major
            }

            // Tile beam is the analog beam. Only HBA can have one analog beam; optional.
            if(parset.settings.anaBeam.enabled)
            {
                vector< double > anaBeamDir(2);
                anaBeamDir[0] = parset.settings.anaBeam.direction.angle1;
                anaBeamDir[1] = parset.settings.anaBeam.direction.angle2;
                itsDALDipole->tileBeam().create(anaBeamDir.size()).set(
                    anaBeamDir);
                itsDALDipole->tileBeamUnit().value = "m";
                itsDALDipole->tileBeamFrame().value = parset.settings.anaBeam
                    .direction.type;

                //itsDALDipole->tileBeamDipoles().create(???.size()).set(???);

                //itsDALDipole->tileCoefUnit().value = ???;
                //itsDALDipole->tileBeamCoefs().value = ???;

                // Relative position within the tile.
                //itsDALDipole->tileDipolePosition().value = ???;
                //itsDALDipole->tileDipolePositionUnit().value = ???;
                //itsDALDipole->tileDipolePositionFrame().value = ???;
            }

            // TODO: TABs: support >1 TABS and add coh/incoh (this is for SAP 0, coh TAB 0), direction (incl type)
            double dpMeas;
            if(!parset.settings.beamFormer.anyCoherentTABs())
            {
                dpMeas = 0.0;
            }
            else
            {
                dpMeas = -1.0;
                for(unsigned sap = 0;
                    sap < parset.settings.beamFormer.SAPs.size(); sap++)
                {
                    for(unsigned tab = 0;
                        tab < parset.settings.beamFormer.SAPs[sap].TABs.size();
                        tab++)
                    {
                        const ObservationSettings::BeamFormer::TAB &t = parset
                            .settings.beamFormer.SAPs[sap].TABs[tab];
                        if(t.coherent)
                        {
                            dpMeas = t.dispersionMeasure;
                            break;
                        }
                    }

                    if(dpMeas != -1.0)
                    {
                        break;
                    }
                }
            }
        }

    /*
     * NOTE: The nTrSamples arg is without the space taken by the crc32 in payload (drop too small frames earlier)
     * and in terms of the transient sample size, i.e. sizeof(int16_t).
     */
    bool TBB_Dipole::crc32tbb(const TBB_Payload* payload, size_t nTrSamples)
    {
      itsCrc32gen.reset();

      const char* ptr = reinterpret_cast<const char*>(payload->data); // to char* for strict-aliasing
      for (unsigned i = 0; i < nTrSamples * sizeof(int16_t); i += 2) {
        int16_t val;
        memcpy(&val, &ptr[i], sizeof val); // strict-aliasing safe
        val = __bswap_16(val);
        itsCrc32gen.process_bytes(&val, sizeof val);
      }

      // It is also possible to process crc32val and see if checksum() equals 0.
      uint32_t crc32val;
      memcpy(&crc32val, &ptr[nTrSamples * sizeof(int16_t)], sizeof crc32val); // idem
#if __BYTE_ORDER == __BIG_ENDIAN
      crc32val = __bswap_32(crc32val);
#endif
      return itsCrc32gen.checksum() == crc32val;
    }
  } // namespace Cobalt
} // namespace LOFAR

