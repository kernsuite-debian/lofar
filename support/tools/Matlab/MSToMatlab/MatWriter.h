#ifndef MatWriter_H
#define MatWriter_H

#include "mat.h"
#include "MSInfo.h"

#include <casacore/casa/Arrays.h>
#include <casacore/casa/BasicMath/Math.h>
#include <casacore/casa/aipstype.h>
#include <casacore/casa/complex.h>

using namespace std;
using namespace casacore;

class MatWriter{
	public:
		MatWriter();
		~MatWriter();
		int openFile(const string& fileName);
		int writeCube(const Cube<complex<float> >& cube);
		int closeFile(const string& varName);
		int writeInfoFile(const string& fileName, MSInfo& msInfo);
		
	private:
		MATFile *matlabDocument;
		mxArray *pa;
		int initMatCube();
		void setCubeSize(int dim1, int dim2, int dim3);

		int dimensions;
//		int* dimensionLengths[];
		int dimensionLengths[3];
};

#endif


