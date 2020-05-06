#ifndef MSInfo_H
#define MSInfo_H

#include <string>
#include <vector>

#include <casacore/casa/Arrays.h>
#include <casacore/casa/aipstype.h>
#include <casacore/casa/complex.h>
#include <casacore/casa/BasicMath/Math.h>

#include "Antenna.h"

class Antenna;

class MSInfo
{
	public:
		MSInfo();
		~MSInfo();

		int nPolarizations;
		
		std::string sourceMS;
		int nChannels;

		casacore::Vector<double> frequencies;

		int nAntennae;
		std::vector<Antenna> antennae;
				
		std::vector<double> timeSlots; // Timeslots that where written to the matlab file
		
		//int nPolarizations;
		bool validInfo;
};

#endif
