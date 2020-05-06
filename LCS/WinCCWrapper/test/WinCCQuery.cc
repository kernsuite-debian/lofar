


#include <cstdlib>
#include <string>
#include <WinCCManager.h>
#include <WinCCResources.h>

#include <vector>
#include <iostream>
#include <Resources.hxx>

#include <boost/program_options.hpp>
#include <boost/any.hpp>



using namespace LOFAR::WINCCWRAPPER;
using namespace std;
namespace po = boost::program_options;

void set_options(po::options_description & description){
    description.add_options()
    ("help", "produce help message")
    ("sql", po::value<std::string>(), "SQL_query")
    ("project", po::value<std::string>(), "WinCC project");

}

int main(int argc, char * argv[])
{
    // Declare the supported options.
    po::options_description desc("Query the WinCCDatabase");
    set_options(desc);

    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);


    if (vm.count("help")) {
        cout << desc << "\n";
        return 1;
    }

    if (vm.count("sql") == 1 && vm.count("project") == 1) {

        const string sql{vm["sql"].as<string>()};

        WinCCResources resource{"WinCCQuery", vm["project"].as<string>(), 0};
        WinCCManager manager;
        cout << "The SQL is: [" << sql << "].\n";

        std::vector<std::vector<std::string>> queryResult;
        manager.get_query(sql, queryResult);
        std::cout<< "RESULTS ----"<<"\n\n";
        std::cout<< "datapoint" << "\t";
        for(auto & row : queryResult){
            for(std::string & column : row){
                std::cout<<column<<"\t";
            }
            std::cout<<"\n";
        }

    } else {
        cout << desc;
    }
}
