#include <UnitTest++.h>
#include <complex>
#include <list>

#include "rspctl.h"

using namespace LOFAR::TYPES;
using namespace LOFAR::rspctl;
using namespace LOFAR::rspctl::utility;

TEST(returns_empty_complex_list_with_empty_string)
{
  std::list<std::complex<double>> list(strtocomplexlist(""));
  CHECK_EQUAL(0, list.size());
}

TEST(returns_list_contains_one_complex_number_when_string_has_a_pair_of_ints)
{
  std::list<std::complex<double>> list(strtocomplexlist("(0,0)"));
  CHECK_EQUAL(1, list.size());
}

TEST(returns_list_contains_two_complex_numbers_when_string_has_two_pairs_of_ints)
{
  std::list<std::complex<double>> list(strtocomplexlist("(0,0),(1,1)"));
  CHECK_EQUAL(2, list.size());
}

TEST(returns_list_contains_two_complex_numbers_when_string_has_two_pairs_of_ints_without_comma)
{
  std::list<std::complex<double>> list(strtocomplexlist("(0,0)(1,1)"));
  CHECK_EQUAL(2, list.size());
}

TEST(returns_list_contains_correct_complex_number_when_string_has_a_pair_of_doubles)
{
  std::list<std::complex<double>> list(strtocomplexlist("(2.3,5.4)"));
  std::complex<double> first_value = list.front();

  CHECK_EQUAL(2.3, first_value.real());
  CHECK_EQUAL(5.4, first_value.imag());
}

TEST(strtocomplexlist_contains_correct_complex_number_when_string_has_a_pair_with_only_a_real_number)
{
  std::list<std::complex<double>> list(strtocomplexlist("(2.3)"));
  std::complex<double> first_value = list.front();

  CHECK_EQUAL(2.3, first_value.real());
  CHECK_EQUAL(0, first_value.imag());
}

/// Here argument parsing for the weights command gets tested. The rspctl
/// expects argc and argv as arguments.
///
// getCommand only returns the created command based on the parsing
// of the argv. It will be deleted by rspctl destructor.
// This is a hack to be able to test the changed WeightsCommand and
// its commandline arguments parsing. Ideally the GCFPort would have
// been mocked out to check the correct behavior but that would have
// taken too much time.

TEST(rspctl_should_create_the_weightscommand_when_weights_option_is_given)
{
  char* argv[2];
  argv[0] =  const_cast<char*>("rspctl");
  argv[1] =  const_cast<char*>("--weights=(1,1)");
  TestableRSPCtl rspctl("RSPCtl", 2, argv);

  Command* command = rspctl.getCommand();
  CHECK_EQUAL(true, (dynamic_cast<WeightsCommand*>(command) != NULL));
}

TEST(rspctl_should_set_weights_correctly_on_command)
{
  char* argv[2];
  argv[0] = const_cast<char*>("rspctl");
  argv[1] = const_cast<char*>("--weights=(0.2,0.1)");
  TestableRSPCtl rspctl("RSPCtl", 2, argv);

  Command* command = rspctl.getCommand();
  WeightsCommand* weights_command = dynamic_cast<WeightsCommand*>(command);
  std::list<std::complex<double>> values = weights_command->getValues();

  CHECK_EQUAL(0.2, values.front().real());
  CHECK_EQUAL(0.1, values.front().imag());
}

int main(int, const char *[])
{
   return UnitTest::RunAllTests();
}
