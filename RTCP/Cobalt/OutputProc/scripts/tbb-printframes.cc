/* tbb-printframes.cc
 * Author: Alexander S. van Amesfoort, ASTRON
 * Last-modified: Aug 2017
 * build: g++ -Wall -o tbb-printframes tbb-printframes.cc
 */

#include <stdint.h>
#include <cstdlib>
#include <cstring>

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>

#include "../src/TBB_Frame.h"

using namespace std;


void timeToStr(time_t t, char* out, size_t out_sz) {
        struct tm *tm = gmtime(&t);
        // Format: Mo, 15-06-2009 20:20:00
        strftime(out, out_sz, "%a, %d-%m-%Y %H:%M:%S", tm);
}

void printHeader(const LOFAR::Cobalt::TBB_Header& h) {
	cout << "Station ID:  " << (uint32_t)h.stationID << endl;
	cout << "RSP ID:      " << (uint32_t)h.rspID << endl;
	cout << "RCU ID:      " << (uint32_t)h.rcuID << endl;
	cout << "Sample Freq: " << (uint32_t)h.sampleFreq << endl;
	cout << "Seq Nr:      " << h.seqNr << endl;
	char buf[32];
	timeToStr(h.time, buf, 32);
	cout << "Time:        " << h.time << " (dd-mm-yyyy: " << buf << " UTC)" << endl;
	bool transient = h.nOfFreqBands == 0;
	if (transient) {
		cout << "Transient" << endl;
		cout << "Sample Nr:   " << h.sampleNr << endl;
	} else {
		cout << "Spectral" << endl;
		cout << "Band Nr:     " << (h.bandSliceNr & LOFAR::Cobalt::TBB_BAND_NR_MASK) << " (real packet headers indicate this may be not the band nr but an index(?))" << endl;
		cout << "Slice Nr:    " << (h.bandSliceNr >> LOFAR::Cobalt::TBB_SLICE_NR_SHIFT) << endl;
	}
	cout << "NSamples/fr: " << h.nOfSamplesPerFrame << endl;
	if (!transient) {
		cout << "NFreq Bands: " << h.nOfFreqBands << endl;

		bool anyBandsPresent = false;
		cout << "Band(s) present: ";
		for (unsigned i = 0; i < 64; i++) {
			for (unsigned j = 0; j < 8; j++) {
				if (h.bandSel[i] & (1 << j)) {
                                        unsigned bandNr = 8 * i + j;
					cout << bandNr << " ";
					anyBandsPresent = true;
				}
			}
		}
		if (!anyBandsPresent) {
			cout << "Warning: Spectral data, but no band present!" << endl;
		} else {
			cout << endl;
		}
	}

	cout << "Spare (0):   " << h.spare << endl;
	cout << "crc16:       " << h.crc16 << endl;
}

void printPayload(const int16_t* payload, size_t payload_len) {
	size_t data_len = payload_len - sizeof(uint32_t) / sizeof(int16_t); // - crc32
	unsigned i;

	if (data_len == 1024) { // transient has 1024 samples + crc32
		for (i = 0; i < data_len; i++) {
			cout << payload[i] << " ";
		}
	} else { // spectral has up to 487 complex samples + crc32
		for (i = 0; i < data_len; i += 2) {
			cout << '(' << payload[i] << ' ' << payload[i+1] << ") "; // assumes data_len is even
		}
	}
	cout << endl;

	cout << "crc32:       " << reinterpret_cast<uint32_t*>(payload[i]) << endl;
}

void printFakeInput() {
	LOFAR::Cobalt::TBB_Header hdr0;

	hdr0.stationID = 1;
	hdr0.rspID = 2;
	hdr0.rcuID = 3;
	hdr0.sampleFreq = 200;
	hdr0.seqNr = 10000;
	hdr0.time = 1380240059;
	hdr0.sampleNrOrBandSliceNr = (17 << LOFAR::Cobalt::TBB_SLICE_NR_SHIFT) | 14; // sliceNr=17; bandNr is 14 (but from real data, the 1st band nr emitted is always 0, so maybe it's an index in the requested (but sorted?) band list?)
	hdr0.nOfSamplesPerFrame = 487;
	hdr0.nOfFreqBands = 487/8 * 2 + 2; // 122, as set in the sb bitmap below

	// subband bitmap
	int i;
	for (i = 0; i < 487/8; i++)
		hdr0.bandSel[i] = 0x41; // in the 1st octet, this corresponds to bands 0 and 6
	for ( ; i < 63; i++)
		hdr0.bandSel[i] = 0;
	hdr0.bandSel[i] = 0x82; // bands 505 and 511

	hdr0.spare = 0;
	hdr0.crc16 = 1; // some val, likely incorrect

	printHeader(hdr0);
}

int main(int argc, char* argv[]) {
	bool printData = false;
	bool fakeInput = false;
	const char* filename = "/dev/stdin";
	int nprinted = 8;

	cout << "Usage: " << argv[0] << " [-d] [-t] [data/tbbdata.raw] [nframes]" << endl;

	int argi = 1;
	if (argc > argi) {
		if (strcmp(argv[argi], "-d") == 0) {
			printData = true;
			argi += 1;
		}

		if (strcmp(argv[argi], "-t") == 0) {
			fakeInput = true;
			argi += 1;
		}

		if (argc > argi) {
			filename = argv[argi];
			argi += 1;
		}

		if (argc > argi) {
			nprinted = std::atoi(argv[argi]);
			argi += 1;
			if (nprinted < 0) {
				cerr << "Bad nframes argument" << endl;
				return 1;
			}
		}
	}


	if (fakeInput) {
		printFakeInput();
		exit(0);
	}

	ifstream ifs(filename);
	if (!ifs) {
		cerr << "Failed to open " << filename << endl;
		return 1;
	}

	cout << "Default frame size:" << " header=" << sizeof(LOFAR::Cobalt::TBB_Header) <<
		" transient=" << sizeof(LOFAR::Cobalt::TBB_Header) + 1024 * sizeof(int16_t) + sizeof(uint32_t) <<
		" spectral=" << sizeof(LOFAR::Cobalt::TBB_Header) + 487 * 2 * sizeof(int16_t) + sizeof(uint32_t) << endl << endl;

	int exit_status = 0;

	// This doesn't work directly with data from message-oriented streams like udp,
	// because header and payload need to be read using a single read() under linux.
	// We don't need that for dumping data from a file; buffers are separate here.
	LOFAR::Cobalt::TBB_Header h;
	int16_t* payload = NULL;
	for (int i = 0; i < nprinted; i++) {
		ifs.read(reinterpret_cast<char*>(&h), sizeof h);
		if (!ifs || static_cast<size_t>(ifs.gcount()) < sizeof h) {
			cerr << "Failed to read " << sizeof h << " frame header bytes from " << filename << endl;
			exit_status = 1;
			goto out;
		}

		printHeader(h);


		size_t payload_len = h.nOfSamplesPerFrame;
		if (h.nOfFreqBands != 0) {
			payload_len *= 2; // spectral has complex nrs, so 2 * int16_t
		}
		payload_len += sizeof(uint32_t) / sizeof(int16_t); // crc32
		if (payload == NULL) {
			// assume this is enough for all future frames; this program is for formatted frame dumps, not for the real thing anyway
			payload = new int16_t[payload_len]; // data + crc32
		}

		ifs.read(reinterpret_cast<char*>(payload), payload_len * sizeof(int16_t));
		if (!ifs) {
			cerr << "Failed to read " << payload_len * sizeof(int16_t) << " frame payload from " << filename << endl;
			exit_status = 1;
			goto out;
		}
		if (printData) {
			printPayload(payload, payload_len);
		}

		cout << "----------------------------" << endl;
	}

out: // too lazy to use proper objects in this test prog, but avoid mem leaks.....
	delete[] payload;
	return exit_status;
}

