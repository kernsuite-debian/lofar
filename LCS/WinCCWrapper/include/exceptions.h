#ifndef WINCC_EXCEPTIONS
#define WINCC_EXCEPTIONS

namespace LOFAR{
namespace WINCCWRAPPER{

class DatapointNameNotFound : public std::exception
{
private:
    std::string message;
public:
    DatapointNameNotFound(const std::string & datapointName):
        message{"Datapoint " + datapointName + " not found"}{}
	const char * what () const throw ()
    {
    	return message.c_str();
    }
};

}
}

#endif
