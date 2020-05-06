#include <lofar_config.h>
#include <Common/LofarLogger.h>
#include <Common/StringUtil.h>
#include <Common/Exception.h>

#include <GCF/TM/GCF_Scheduler.h>

#include "rspctl.h"

#include <sstream>

using namespace LOFAR;
using namespace LOFAR::rspctl;
using namespace LOFAR::GCF::TM;
using namespace std;

int main(int argc, char** argv)
{
	GCFScheduler::instance()->init(argc, argv, "rspctl");

	// Log command line to track usage
	stringstream s;
	for (int i = 0; i < argc; i++)
	  s << argv[i] << " ";
	LOG_INFO_STR("Command line: " << s.str());

	LOG_INFO(formatString("Program %s has started", argv[0]));

	RSPCtl c("RSPCtl", argc, argv);

	try {
		c.start(); // make initial transition
		GCFScheduler::instance()->run();
	}
	catch (Exception& e) {
		cerr << "Exception: " << e.text() << endl;
		exit(EXIT_FAILURE);
	}

	LOG_INFO("Normal termination of program");

	return (c.getExitCode());
}
