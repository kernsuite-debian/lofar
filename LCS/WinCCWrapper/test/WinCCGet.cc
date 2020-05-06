#include <cstdlib>
#include <string>
#include <WinCCWrapper.h>
#include <vector>
#include <iostream>
#include <Resources.hxx>

using namespace LOFAR::WINCCWRAPPER;
using namespace std;

void get_help(){
    cout << "Usage:" << endl;
    cout << "WinCCGet \"datapoint_name\" datapoint_type project_name" << endl;
    cout << "Accepted datapoint types:" << endl;
    cout << "  int, float, string, list (for int lists)" << endl;
}

int main(int argc, char * argv[])
{
  bool asking_for_help = ((argc < 4) && (string(argv[1]) == "--help" || string(argv[1]) == "--h"));
  bool invalid_args = (argc != 4);

  if (asking_for_help || invalid_args){
    get_help();
    return 0;
  }
  WinCCWrapper wrapper{std::string(argv[3])};
  string dpname{argv[1]};

  if (string(argv[2]) == "int") {
    int value;
    value = wrapper.get_datapoint_int(dpname);
    cout << dpname << ": " << value << endl;
  }
  else if (string(argv[2]) == "float") {
    float value;
    value = wrapper.get_datapoint_float(dpname);
    cout << dpname << ": " << value << endl;
  }
  else if (string(argv[2]) == "string") {
    string value;
    value = wrapper.get_datapoint_string(dpname);
    cout << dpname << ": " << value << endl;
  }
  else if (string(argv[2]) == "list") {
    // We use the argument 'list' for consistency with the python interface,
    // even though we must pass a vector
    std::vector<int> value;
    value = wrapper.get_datapoint_vector(dpname);

    cout << dpname << ": [";
    for (auto iter = value.cbegin(); iter != value.cend(); iter++) {
      cout << *iter << ", ";
    }
    cout << "\b\b]" << endl; // remove the last ', ' from the end.
  }
  else {
    cout << "Unknown datatype: " << string(argv[2]) << "\n" << endl;
    get_help();
  }
  return 0;
}
