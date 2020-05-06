#ifndef MSReaderH
#define MSReaderH

#include "MSInfo.h"

#include <casacore/ms/MeasurementSets.h>

#include <casacore/tables/Tables.h>

#include <casacore/casa/Arrays.h>
#include <casacore/casa/aipstype.h>
#include <casacore/casa/complex.h>

#include <string>

using namespace std;
using namespace casacore;

class MSReader
{
	public:
		MSReader(const string& msName);
		~MSReader();
		int getNumberAntennae();
		Cube<complex<float> > getTimeCube			(int timeSlot , int selectedBand, int polarizationID, int startFreq		 , int stopFreq    );
		Cube<complex<float> > getFrequencyCube(int frequency, int selectedBand, int polarizationID, int startTimeSlot, int stopTimeSlot);
		void setBandInfo(int bandID);
		MSInfo& getMSInfo();

		int getNTimeSlots();
	private:
		string msName;
		MeasurementSet* ms;
		//int nAntennae;
		int bandsPerTimeSlot;
		int nTimeSlots; // Available timeslots in MS
		MSInfo msInfo;
		
};


#endif

