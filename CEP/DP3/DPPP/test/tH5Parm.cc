#include <DPPP/H5Parm.h>
#include <iostream>
#include <sstream>
#include <stdio.h>
#include <vector>
#include <Common/LofarLogger.h>
#include <casacore/casa/BasicMath/Math.h>

using namespace std;
using namespace LOFAR;

void checkAxes(H5Parm::SolTab& soltab) {
  ASSERT(soltab.nAxes()==3);
  ASSERT(soltab.hasAxis("ant"));
  ASSERT(soltab.hasAxis("time"));
  ASSERT(soltab.hasAxis("bla"));
  ASSERT(soltab.getAxis(0).name=="ant");
  ASSERT(soltab.getAxis(1).name=="time");
  ASSERT(soltab.getAxis(2).name=="bla");
  ASSERT(soltab.getAxis(0).size==3);
  ASSERT(soltab.getAxis(1).size==4);
  ASSERT(soltab.getAxis(2).size==1);
}

int main(int, char**) {
  {
    {
      // Create a new H5Parm
      cout<<"Create tH5Parm_tmp.h5"<<endl;
      H5Parm h5parm("tH5Parm_tmp.h5");

      // Check that something is created
      ASSERT(((H5::H5File&)(h5parm)).getNumObjs()==1);

      // Check the name of the new solset "sol000"
      ASSERT(h5parm.getSolSetName()=="sol000");

      // Add some metadata
      vector<string> antNames;
      vector<double> oneAntPos(3);
      vector<vector<double> > antPositions;
      for (uint i=0; i<5; ++i) {
        stringstream antNameStr;
        antNameStr<<"Antenna"<<i;
        antNames.push_back(antNameStr.str());
        antPositions.push_back(oneAntPos);
      }
      h5parm.addAntennas(antNames, antPositions);

      vector<H5Parm::AxisInfo> axes;
      axes.push_back(H5Parm::AxisInfo("ant",3));
      axes.push_back(H5Parm::AxisInfo("time",4));
      axes.push_back(H5Parm::AxisInfo("bla",1));

      cout<<"Create new SolTab"<<endl;
      H5Parm::SolTab a = h5parm.createSolTab("mysol","mytype",axes);

      // Check that the soltab exists
      ASSERT(h5parm.nSolTabs() == 1);
      ASSERT(h5parm.hasSolTab("mysol"));

      // Check the axes
      H5Parm::SolTab soltab = h5parm.getSolTab("mysol");
      ASSERT(soltab.getType()=="mytype");
      checkAxes(soltab);

      // Add some data
      vector<double> vals(3*4);
      for (size_t ant=0; ant<3; ++ant)
        for (size_t time=0; time<4; ++time)
          vals[ant*4+time]=10*ant+time;
      soltab.setValues(vals, vector<double>());

      // Add metadata for stations
      vector<string> someAntNames;
      someAntNames.push_back("Antenna1");
      someAntNames.push_back("Antenna2");
      someAntNames.push_back("Antenna3");
      soltab.setAntennas(someAntNames);

      // Add metadata for times
      vector<double> times;
      times.push_back(57878.5);
      times.push_back(57880.5);
      times.push_back(57882.5);
      soltab.setTimes(times);
    }

    {
      cout<<"opening tH5Parm_tmp.h5 again, force a new soltab"<<endl;
      H5Parm h5parm("tH5Parm_tmp.h5", true);
      ASSERT(h5parm.getSolSetName()=="sol001");
    }

    {
      cout<<"opening tH5Parm_tmp.h5 again, force a new solset with name"<<endl;
      H5Parm h5parm("tH5Parm_tmp.h5", true, "harry");
      ASSERT(h5parm.getSolSetName()=="harry");
    }

    {
      cout<<"opening tH5Parm_tmp.h5 again, read existing soltab"<<endl;
      H5Parm h5parm("tH5Parm_tmp.h5", false, "sol000");
      ASSERT(h5parm.getSolSetName()=="sol000");
      ASSERT(h5parm.nSolTabs() == 1);
      ASSERT(h5parm.hasSolTab("mysol"));
      ASSERT(!h5parm.hasSolTab("nonexistingsol"));

      // Check the axes
      H5Parm::SolTab soltab = h5parm.getSolTab("mysol");
      ASSERT(soltab.getType()=="mytype");
      checkAxes(soltab);

      cout<<"read some data"<<endl;
      double starttime = 57878.49999;
      hsize_t starttimeindex = soltab.getTimeIndex(starttime);
      cout<<"starttimeindex="<<starttimeindex<<endl;
      vector<double> val = soltab.getValues("Antenna2", starttimeindex, 4);
      ASSERT(casa::near(val[0],10.));
      ASSERT(casa::near(val[1],11.));
      ASSERT(casa::near(val[2],12.));
      ASSERT(casa::near(val[3],13.));
      cout<<"read some data with stride 2"<<endl;
      starttime = 57880.5;
      starttimeindex = soltab.getTimeIndex(starttime);
      ASSERT(starttimeindex==1);
      vector<double> val2 = soltab.getValues("Antenna3", starttimeindex, 2, 2);
      ASSERT(casa::near(val2[0],21.));
      ASSERT(casa::near(val2[1],23.));
      cout<<"testing stride"<<endl;
      ASSERT(casa::near(soltab.getTimeInterval(),2.));
      vector<string> antennas = soltab.getStringAxis("ant");
      cout<<"reading the antennas into a vector"<<endl;
      ASSERT(antennas.size()==3);
      ASSERT(antennas[0]=="Antenna1");
      ASSERT(antennas[1]=="Antenna2");
      ASSERT(antennas[2]=="Antenna3");
    }

    // Remove the file
//    remove("tH5Parm_tmp.h5");
  }

  return 0;
}
