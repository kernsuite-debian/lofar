#include "lofar_config.h"
#include <Common/LofarTypes.h>

#include <MessageBus/Util.h>

#include <stdlib.h>

using namespace qpid::messaging;
using namespace std;

namespace {
  string getenv_str(const char *env) {
    char *val = getenv(env);
    return string(val ? val : "");
  }
}

namespace LOFAR {
  Duration TimeOutDuration(double secs)
  {
    if (secs > 0.0)
      return (Duration)(static_cast<uint64>(1000.0 * secs));

    return Duration::FOREVER;
  }

  std::string queue_prefix()
  {
    string lofarenv = getenv_str("LOFARENV");
    string queueprefix = getenv_str("QUEUE_PREFIX");

    if (lofarenv == "PRODUCTION") {
    } else if (lofarenv == "TEST") {
      queueprefix += "test.";
    } else {
      queueprefix += "devel.";
    }

    return queueprefix;
  }

  std::string broker_state()
  {
    string lofarenv = getenv_str("LOFARENV");

    if (lofarenv == "PRODUCTION") {
      return "ccu001.control.lofar";
    } else if (lofarenv == "TEST") {
      return "ccu199.control.lofar";
    } else {
      return "localhost";
    }
  }

  std::string broker_feedback()
  {
    string lofarenv = getenv_str("LOFARENV");

    if (lofarenv == "PRODUCTION") {
      return "mcu001.control.lofar";
    } else if (lofarenv == "TEST") {
      return "mcu199.control.lofar";
    } else {
      return "localhost";
    }
  }
} // namespace LOFAR

