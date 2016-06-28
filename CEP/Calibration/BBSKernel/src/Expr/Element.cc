//# Element.cc: A scalar field that transparantly handles 0-D (constant) and
//# 2-D fields.
//#
//# Copyright (C) 2009
//# ASTRON (Netherlands Foundation for Research in Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//#
//# This program is free software; you can redistribute it and/or modify
//# it under the terms of the GNU General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or
//# (at your option) any later version.
//#
//# This program is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License
//# along with this program; if not, write to the Free Software
//# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//# $Id: Element.cc 30919 2015-02-05 15:26:22Z amesfoort $

#include <lofar_config.h>
#include <BBSKernel/Expr/Element.h>

namespace LOFAR
{
namespace BBS
{

Element::Element()
    :   RefCounted<ElementImpl>(new ElementImpl())
{
}

} //# namespace BBS
} //# namespace LOFAR
