//#  MessageContent.cc: one_line_description
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

//# Always #include <lofar_config.h> first!
#include <lofar_config.h>

//# Includes
#include <MessageBus/Exceptions.h>
#include <MessageBus/XMLDoc.h>

#include <Common/LofarLogger.h>
#include <Common/StringUtil.h>

using namespace std;
using namespace LOFAR::StringUtil;

namespace LOFAR {

XMLDoc::XMLDoc(const std::string &content)
{
  itsContent = content;
}

XMLDoc::XMLDoc(const XMLDoc &other, const std::string &key)
{
  const string content = other.getXMLvalue(key);

  // Extract root element (last element in 'key')
  const vector<string> labels = split(key, '/');
  ASSERT(!labels.empty());
  const string root_element = labels[labels.size()-1];

  itsContent = formatString("<%s>%s</%s>", root_element.c_str(), other.getXMLvalue(key).c_str(), root_element.c_str());
}

XMLDoc::~XMLDoc()
{
}

std::string XMLDoc::getContent() const
{
  return itsContent;
}

string XMLDoc::getXMLvalue(const string& key) const
{
  // get copy of content
  vector<string>  labels = split(key, '/');

  // loop over subkeys
  string::size_type  offset = 0;
  string::size_type  begin = string::npos;
  string::size_type  end = string::npos;
  string        startTag;
  for (size_t i = 0; i <  labels.size(); ++i) {
    // define tags to find
    startTag = string("<"+labels[i]+">");
    // search begin tag
    begin  = itsContent.find(startTag, offset);
    if (begin == string::npos) {
      THROW(XMLException, "XML element not found (could not find begin tag): " << key);
    }
    offset = begin;
  }
  // search end tag
  string stopTag ("</"+labels[labels.size()-1]+">");
  begin+=startTag.size();
  end = itsContent.find(stopTag, begin);
  if (end == string::npos) {
    THROW(XMLException, "XML element not found (could not find end tag): " << key);
  }
  return (itsContent.substr(begin, end - begin));
}

void XMLDoc::setXMLvalue(const string& key, const string &data)
{
  // get copy of content
  vector<string>  labels = split(key, '/');

  // loop over subkeys
  string::size_type  offset = 0;
  string::size_type  begin = string::npos;
  string::size_type  end = string::npos;
  string        startTag;
  for (size_t i = 0; i <  labels.size(); ++i) {
    // define tags to find
    startTag = string("<"+labels[i]+">");
    // search begin tag
    begin  = itsContent.find(startTag, offset);
    if (begin == string::npos) {
      THROW(XMLException, "XML element not found (could not find begin tag): " << key);
    }
    offset = begin;
  }
  // search end tag
  string stopTag ("</"+labels[labels.size()-1]+">");
  begin+=startTag.size();
  end = itsContent.find(stopTag, begin);
  if (end == string::npos) {
    THROW(XMLException, "XML element not found (could not find end tag): " << key);
  }

  itsContent.replace(begin, end - begin, data);
}

void XMLDoc::insertXML(const string &key, const string &xml)
{
  setXMLvalue(key, xml);
}

} // namespace LOFAR
