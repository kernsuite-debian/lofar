#include <cstdlib>
#include <string>
#include <WinCCWrapper.h>
#include <vector>

using namespace LOFAR::WINCCWRAPPER;
using namespace std;

void get_help(){
    cout << "Usage:" << endl;
    cout << "WinCCSet \"datapoint_name\" datapoint_type new_value" << endl;
    cout << "Accepted datapoint types:" << endl;
    cout << "  int, float, string, list (for int list)" << endl;
}

int main(int argc, char * argv[])
{
  bool asking_for_help = ((argc == 2) && (string(argv[1]) == "--help" || string(argv[1]) == "--h"));
  bool invalid_args = (argc < 4);

  if (asking_for_help || invalid_args){
    get_help();
    return 0;
  }
  WinCCWrapper wrapper{""};
  string dpname{argv[1]};

  if (string(argv[2]) == "float") {
    float value = atof(argv[3]);
    wrapper.set_datapoint(dpname, value);
  }
  else if (string(argv[2]) == "int") {
    int value = atoi(argv[3]);
    wrapper.set_datapoint(dpname, value);
  }
  else if (string(argv[2]) == "string") {
    string value{argv[3]};
    wrapper.set_datapoint(dpname, value);
  }
  else if (string(argv[2]) == "list") {
    // we cannot append to lists made outside of a boost python module declaration,
    // so we pass a vector instead.
    // We use the argument "list" for consistency with the python interface
    vector<int> value(argc-3);

    for (int i = 3; i < argc; i++) {
      value[i-3] = atoi(argv[i]);
    }

    wrapper.set_datapoint(dpname, value);
  }
  else {
    cout << "Unknown datatype: " << string(argv[2]) << "\n" << endl;
    get_help();
  }
  return 0;
}

