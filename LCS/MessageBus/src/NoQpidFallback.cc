//# NoQpidFallback.cc: A fake implementation of the QPID API in case QPID is not installed
//#
//# Copyright (C) 2015
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR software suite.
//# The LOFAR software suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published
//# by the Free Software Foundation, either version 3 of the License, or
//# (at your option) any later version.
//#
//# The LOFAR software suite is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along
//# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
//#
//# $Id: NoQpidFallback.cc 31371 2015-03-27 10:31:19Z mol $

#include <lofar_config.h>

#ifndef HAVE_QPID
#include <MessageBus/NoQpidFallback.h>

std::ostream& operator<<(std::ostream& out, const qpid::types::Variant& value) {
  (void)value;
  return out;
}

std::ostream& operator<<(std::ostream& out, const qpid::types::Variant::Map& map) {
  (void)map;
  return out;
}

std::ostream& operator<<(std::ostream& out, const qpid::types::Variant::List& list) {
  (void)list;
  return out;
}

#endif

