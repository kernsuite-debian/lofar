# ./ltasip.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:4d7a8ef1458fc65d34d2aea044869f9c907a2072
# Generated 2017-04-05 12:06:22.893714 by PyXB version 1.2.5 using Python 2.7.6.final.0
# Namespace http://www.astron.nl/SIP-Lofar


import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:8579f6ca-19e7-11e7-9dbf-28d2444d27e5')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.5'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('http://www.astron.nl/SIP-Lofar', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: {http://www.astron.nl/SIP-Lofar}FrequencyUnit
class FrequencyUnit (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FrequencyUnit')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 24, 1)
    _Documentation = None
FrequencyUnit._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FrequencyUnit, enum_prefix=None)
FrequencyUnit.Hz = FrequencyUnit._CF_enumeration.addEnumeration(unicode_value='Hz', tag='Hz')
FrequencyUnit.kHz = FrequencyUnit._CF_enumeration.addEnumeration(unicode_value='kHz', tag='kHz')
FrequencyUnit.MHz = FrequencyUnit._CF_enumeration.addEnumeration(unicode_value='MHz', tag='MHz')
FrequencyUnit.GHz = FrequencyUnit._CF_enumeration.addEnumeration(unicode_value='GHz', tag='GHz')
FrequencyUnit._InitializeFacetMap(FrequencyUnit._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'FrequencyUnit', FrequencyUnit)
_module_typeBindings.FrequencyUnit = FrequencyUnit

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}LengthUnit
class LengthUnit (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LengthUnit')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 39, 1)
    _Documentation = None
LengthUnit._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=LengthUnit, enum_prefix=None)
LengthUnit.m = LengthUnit._CF_enumeration.addEnumeration(unicode_value='m', tag='m')
LengthUnit.km = LengthUnit._CF_enumeration.addEnumeration(unicode_value='km', tag='km')
LengthUnit._InitializeFacetMap(LengthUnit._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'LengthUnit', LengthUnit)
_module_typeBindings.LengthUnit = LengthUnit

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}TimeUnit
class TimeUnit (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TimeUnit')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 52, 1)
    _Documentation = None
TimeUnit._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TimeUnit, enum_prefix=None)
TimeUnit.s = TimeUnit._CF_enumeration.addEnumeration(unicode_value='s', tag='s')
TimeUnit.ms = TimeUnit._CF_enumeration.addEnumeration(unicode_value='ms', tag='ms')
TimeUnit.us = TimeUnit._CF_enumeration.addEnumeration(unicode_value='us', tag='us')
TimeUnit.ns = TimeUnit._CF_enumeration.addEnumeration(unicode_value='ns', tag='ns')
TimeUnit._InitializeFacetMap(TimeUnit._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'TimeUnit', TimeUnit)
_module_typeBindings.TimeUnit = TimeUnit

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}AngleUnit
class AngleUnit (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AngleUnit')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 67, 1)
    _Documentation = None
AngleUnit._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=AngleUnit, enum_prefix=None)
AngleUnit.radians = AngleUnit._CF_enumeration.addEnumeration(unicode_value='radians', tag='radians')
AngleUnit.degrees = AngleUnit._CF_enumeration.addEnumeration(unicode_value='degrees', tag='degrees')
AngleUnit.arcsec = AngleUnit._CF_enumeration.addEnumeration(unicode_value='arcsec', tag='arcsec')
AngleUnit._InitializeFacetMap(AngleUnit._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'AngleUnit', AngleUnit)
_module_typeBindings.AngleUnit = AngleUnit

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}PixelUnit
class PixelUnit (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PixelUnit')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 81, 1)
    _Documentation = None
PixelUnit._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=PixelUnit, enum_prefix=None)
PixelUnit.Jybeam = PixelUnit._CF_enumeration.addEnumeration(unicode_value='Jy/beam', tag='Jybeam')
PixelUnit._InitializeFacetMap(PixelUnit._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'PixelUnit', PixelUnit)
_module_typeBindings.PixelUnit = PixelUnit

# List simple type: {http://www.astron.nl/SIP-Lofar}ListOfDouble
# superclasses pyxb.binding.datatypes.anySimpleType
class ListOfDouble (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.double."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ListOfDouble')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 93, 1)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.double
ListOfDouble._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'ListOfDouble', ListOfDouble)
_module_typeBindings.ListOfDouble = ListOfDouble

# List simple type: {http://www.astron.nl/SIP-Lofar}ListOfString
# superclasses pyxb.binding.datatypes.anySimpleType
class ListOfString (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.string."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ListOfString')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 96, 1)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.string
ListOfString._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'ListOfString', ListOfString)
_module_typeBindings.ListOfString = ListOfString

# List simple type: {http://www.astron.nl/SIP-Lofar}ListOfSubbands
# superclasses pyxb.binding.datatypes.anySimpleType
class ListOfSubbands (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.unsignedShort."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ListOfSubbands')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 99, 1)
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.unsignedShort
ListOfSubbands._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', 'ListOfSubbands', ListOfSubbands)
_module_typeBindings.ListOfSubbands = ListOfSubbands

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}EquinoxType
class EquinoxType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'EquinoxType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 120, 1)
    _Documentation = None
EquinoxType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=EquinoxType, enum_prefix=None)
EquinoxType.B1950 = EquinoxType._CF_enumeration.addEnumeration(unicode_value='B1950', tag='B1950')
EquinoxType.J2000 = EquinoxType._CF_enumeration.addEnumeration(unicode_value='J2000', tag='J2000')
EquinoxType.SUN = EquinoxType._CF_enumeration.addEnumeration(unicode_value='SUN', tag='SUN')
EquinoxType.JUPITER = EquinoxType._CF_enumeration.addEnumeration(unicode_value='JUPITER', tag='JUPITER')
EquinoxType._InitializeFacetMap(EquinoxType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'EquinoxType', EquinoxType)
_module_typeBindings.EquinoxType = EquinoxType

# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 158, 4)
    _Documentation = None
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.WGS84 = STD_ANON._CF_enumeration.addEnumeration(unicode_value='WGS84', tag='WGS84')
STD_ANON.ITRF2000 = STD_ANON._CF_enumeration.addEnumeration(unicode_value='ITRF2000', tag='ITRF2000')
STD_ANON.ITRF2005 = STD_ANON._CF_enumeration.addEnumeration(unicode_value='ITRF2005', tag='ITRF2005')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)
_module_typeBindings.STD_ANON = STD_ANON

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}AntennaFieldType
class AntennaFieldType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AntennaFieldType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 186, 1)
    _Documentation = None
AntennaFieldType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=AntennaFieldType, enum_prefix=None)
AntennaFieldType.HBA0 = AntennaFieldType._CF_enumeration.addEnumeration(unicode_value='HBA0', tag='HBA0')
AntennaFieldType.HBA1 = AntennaFieldType._CF_enumeration.addEnumeration(unicode_value='HBA1', tag='HBA1')
AntennaFieldType.HBA = AntennaFieldType._CF_enumeration.addEnumeration(unicode_value='HBA', tag='HBA')
AntennaFieldType.LBA = AntennaFieldType._CF_enumeration.addEnumeration(unicode_value='LBA', tag='LBA')
AntennaFieldType._InitializeFacetMap(AntennaFieldType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'AntennaFieldType', AntennaFieldType)
_module_typeBindings.AntennaFieldType = AntennaFieldType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}StationTypeType
class StationTypeType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'StationTypeType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 197, 1)
    _Documentation = None
StationTypeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=StationTypeType, enum_prefix=None)
StationTypeType.Core = StationTypeType._CF_enumeration.addEnumeration(unicode_value='Core', tag='Core')
StationTypeType.Remote = StationTypeType._CF_enumeration.addEnumeration(unicode_value='Remote', tag='Remote')
StationTypeType.International = StationTypeType._CF_enumeration.addEnumeration(unicode_value='International', tag='International')
StationTypeType._InitializeFacetMap(StationTypeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'StationTypeType', StationTypeType)
_module_typeBindings.StationTypeType = StationTypeType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}ProcessRelationType
class ProcessRelationType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ProcessRelationType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 239, 1)
    _Documentation = None
ProcessRelationType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ProcessRelationType, enum_prefix=None)
ProcessRelationType.GroupID = ProcessRelationType._CF_enumeration.addEnumeration(unicode_value='GroupID', tag='GroupID')
ProcessRelationType._InitializeFacetMap(ProcessRelationType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ProcessRelationType', ProcessRelationType)
_module_typeBindings.ProcessRelationType = ProcessRelationType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}FilterSelectionType
class FilterSelectionType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FilterSelectionType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 274, 1)
    _Documentation = None
FilterSelectionType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FilterSelectionType, enum_prefix=None)
FilterSelectionType.n10_70_MHz = FilterSelectionType._CF_enumeration.addEnumeration(unicode_value='10-70 MHz', tag='n10_70_MHz')
FilterSelectionType.n10_90_MHz = FilterSelectionType._CF_enumeration.addEnumeration(unicode_value='10-90 MHz', tag='n10_90_MHz')
FilterSelectionType.n30_70_MHz = FilterSelectionType._CF_enumeration.addEnumeration(unicode_value='30-70 MHz', tag='n30_70_MHz')
FilterSelectionType.n30_90_MHz = FilterSelectionType._CF_enumeration.addEnumeration(unicode_value='30-90 MHz', tag='n30_90_MHz')
FilterSelectionType.n110_190_MHz = FilterSelectionType._CF_enumeration.addEnumeration(unicode_value='110-190 MHz', tag='n110_190_MHz')
FilterSelectionType.n170_230_MHz = FilterSelectionType._CF_enumeration.addEnumeration(unicode_value='170-230 MHz', tag='n170_230_MHz')
FilterSelectionType.n210_250_MHz = FilterSelectionType._CF_enumeration.addEnumeration(unicode_value='210-250 MHz', tag='n210_250_MHz')
FilterSelectionType._InitializeFacetMap(FilterSelectionType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'FilterSelectionType', FilterSelectionType)
_module_typeBindings.FilterSelectionType = FilterSelectionType

# Atomic simple type: [anonymous]
class STD_ANON_ (pyxb.binding.datatypes.double, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 285, 1)
    _Documentation = None
STD_ANON_._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_, enum_prefix=None)
STD_ANON_._CF_enumeration.addEnumeration(unicode_value='160', tag=None)
STD_ANON_._CF_enumeration.addEnumeration(unicode_value='200', tag=None)
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_enumeration)
_module_typeBindings.STD_ANON_ = STD_ANON_

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}AntennaSetType
class AntennaSetType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AntennaSetType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 294, 1)
    _Documentation = None
AntennaSetType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=AntennaSetType, enum_prefix=None)
AntennaSetType.HBA_Zero = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA Zero', tag='HBA_Zero')
AntennaSetType.HBA_One = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA One', tag='HBA_One')
AntennaSetType.HBA_Dual = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA Dual', tag='HBA_Dual')
AntennaSetType.HBA_Joined = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA Joined', tag='HBA_Joined')
AntennaSetType.LBA_Outer = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='LBA Outer', tag='LBA_Outer')
AntennaSetType.LBA_Inner = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='LBA Inner', tag='LBA_Inner')
AntennaSetType.LBA_Sparse_Even = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='LBA Sparse Even', tag='LBA_Sparse_Even')
AntennaSetType.LBA_Sparse_Odd = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='LBA Sparse Odd', tag='LBA_Sparse_Odd')
AntennaSetType.LBA_X = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='LBA X', tag='LBA_X')
AntennaSetType.LBA_Y = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='LBA Y', tag='LBA_Y')
AntennaSetType.HBA_Zero_Inner = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA Zero Inner', tag='HBA_Zero_Inner')
AntennaSetType.HBA_One_Inner = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA One Inner', tag='HBA_One_Inner')
AntennaSetType.HBA_Dual_Inner = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA Dual Inner', tag='HBA_Dual_Inner')
AntennaSetType.HBA_Joined_Inner = AntennaSetType._CF_enumeration.addEnumeration(unicode_value='HBA Joined Inner', tag='HBA_Joined_Inner')
AntennaSetType._InitializeFacetMap(AntennaSetType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'AntennaSetType', AntennaSetType)
_module_typeBindings.AntennaSetType = AntennaSetType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}StationSelectionType
class StationSelectionType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'StationSelectionType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 312, 1)
    _Documentation = None
StationSelectionType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=StationSelectionType, enum_prefix=None)
StationSelectionType.Single = StationSelectionType._CF_enumeration.addEnumeration(unicode_value='Single', tag='Single')
StationSelectionType.Core = StationSelectionType._CF_enumeration.addEnumeration(unicode_value='Core', tag='Core')
StationSelectionType.Dutch = StationSelectionType._CF_enumeration.addEnumeration(unicode_value='Dutch', tag='Dutch')
StationSelectionType.International = StationSelectionType._CF_enumeration.addEnumeration(unicode_value='International', tag='International')
StationSelectionType.Custom = StationSelectionType._CF_enumeration.addEnumeration(unicode_value='Custom', tag='Custom')
StationSelectionType._InitializeFacetMap(StationSelectionType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'StationSelectionType', StationSelectionType)
_module_typeBindings.StationSelectionType = StationSelectionType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}ObservingModeType
class ObservingModeType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ObservingModeType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 321, 1)
    _Documentation = None
ObservingModeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ObservingModeType, enum_prefix=None)
ObservingModeType.Interferometer = ObservingModeType._CF_enumeration.addEnumeration(unicode_value='Interferometer', tag='Interferometer')
ObservingModeType.Beam_Observation = ObservingModeType._CF_enumeration.addEnumeration(unicode_value='Beam Observation', tag='Beam_Observation')
ObservingModeType.TBB_standalone = ObservingModeType._CF_enumeration.addEnumeration(unicode_value='TBB (standalone)', tag='TBB_standalone')
ObservingModeType.TBB_piggyback = ObservingModeType._CF_enumeration.addEnumeration(unicode_value='TBB (piggyback)', tag='TBB_piggyback')
ObservingModeType.Direct_Data_Storage = ObservingModeType._CF_enumeration.addEnumeration(unicode_value='Direct Data Storage', tag='Direct_Data_Storage')
ObservingModeType.Non_Standard = ObservingModeType._CF_enumeration.addEnumeration(unicode_value='Non Standard', tag='Non_Standard')
ObservingModeType.Unknown = ObservingModeType._CF_enumeration.addEnumeration(unicode_value='Unknown', tag='Unknown')
ObservingModeType._InitializeFacetMap(ObservingModeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ObservingModeType', ObservingModeType)
_module_typeBindings.ObservingModeType = ObservingModeType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}TimeSystemType
class TimeSystemType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TimeSystemType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 332, 1)
    _Documentation = None
TimeSystemType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TimeSystemType, enum_prefix=None)
TimeSystemType.UTC = TimeSystemType._CF_enumeration.addEnumeration(unicode_value='UTC', tag='UTC')
TimeSystemType.LST = TimeSystemType._CF_enumeration.addEnumeration(unicode_value='LST', tag='LST')
TimeSystemType._InitializeFacetMap(TimeSystemType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'TimeSystemType', TimeSystemType)
_module_typeBindings.TimeSystemType = TimeSystemType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}ProcessingType
class ProcessingType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ProcessingType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 420, 1)
    _Documentation = None
ProcessingType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ProcessingType, enum_prefix=None)
ProcessingType.Correlator = ProcessingType._CF_enumeration.addEnumeration(unicode_value='Correlator', tag='Correlator')
ProcessingType.Coherent_Stokes = ProcessingType._CF_enumeration.addEnumeration(unicode_value='Coherent Stokes', tag='Coherent_Stokes')
ProcessingType.Incoherent_Stokes = ProcessingType._CF_enumeration.addEnumeration(unicode_value='Incoherent Stokes', tag='Incoherent_Stokes')
ProcessingType.Flys_Eye = ProcessingType._CF_enumeration.addEnumeration(unicode_value="Fly's Eye", tag='Flys_Eye')
ProcessingType.Non_Standard = ProcessingType._CF_enumeration.addEnumeration(unicode_value='Non Standard', tag='Non_Standard')
ProcessingType._InitializeFacetMap(ProcessingType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ProcessingType', ProcessingType)
_module_typeBindings.ProcessingType = ProcessingType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}MeasurementType
class MeasurementType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'MeasurementType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 429, 1)
    _Documentation = None
MeasurementType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=MeasurementType, enum_prefix=None)
MeasurementType.Test = MeasurementType._CF_enumeration.addEnumeration(unicode_value='Test', tag='Test')
MeasurementType.Tune_Up = MeasurementType._CF_enumeration.addEnumeration(unicode_value='Tune Up', tag='Tune_Up')
MeasurementType.Calibration = MeasurementType._CF_enumeration.addEnumeration(unicode_value='Calibration', tag='Calibration')
MeasurementType.Target = MeasurementType._CF_enumeration.addEnumeration(unicode_value='Target', tag='Target')
MeasurementType.All_Sky = MeasurementType._CF_enumeration.addEnumeration(unicode_value='All Sky', tag='All_Sky')
MeasurementType.Miscellaneous = MeasurementType._CF_enumeration.addEnumeration(unicode_value='Miscellaneous', tag='Miscellaneous')
MeasurementType._InitializeFacetMap(MeasurementType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'MeasurementType', MeasurementType)
_module_typeBindings.MeasurementType = MeasurementType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}PulsarSelectionType
class PulsarSelectionType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PulsarSelectionType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 647, 1)
    _Documentation = None
PulsarSelectionType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=PulsarSelectionType, enum_prefix=None)
PulsarSelectionType.Pulsars_in_observation_specs_file_or_SAP = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Pulsars in observation specs, file or SAP', tag='Pulsars_in_observation_specs_file_or_SAP')
PulsarSelectionType.Pulsars_in_observation_specs = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Pulsars in observation specs', tag='Pulsars_in_observation_specs')
PulsarSelectionType.Pulsar_specified_in_dataproduct = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Pulsar specified in dataproduct', tag='Pulsar_specified_in_dataproduct')
PulsarSelectionType.Brightest_known_pulsar_in_SAP = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Brightest known pulsar in SAP', tag='Brightest_known_pulsar_in_SAP')
PulsarSelectionType.Three_brightest_known_pulsars_in_SAP = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Three brightest known pulsars in SAP', tag='Three_brightest_known_pulsars_in_SAP')
PulsarSelectionType.Brightest_known_pulsar_in_TAB = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Brightest known pulsar in TAB', tag='Brightest_known_pulsar_in_TAB')
PulsarSelectionType.Pulsars_in_observation_specs_file_and_brightest_in_SAP_and_TAB = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Pulsars in observation specs, file and brightest in SAP and TAB', tag='Pulsars_in_observation_specs_file_and_brightest_in_SAP_and_TAB')
PulsarSelectionType.Specified_pulsar_list = PulsarSelectionType._CF_enumeration.addEnumeration(unicode_value='Specified pulsar list', tag='Specified_pulsar_list')
PulsarSelectionType._InitializeFacetMap(PulsarSelectionType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'PulsarSelectionType', PulsarSelectionType)
_module_typeBindings.PulsarSelectionType = PulsarSelectionType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}DataProductType
class DataProductType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DataProductType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 705, 1)
    _Documentation = None
DataProductType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=DataProductType, enum_prefix=None)
DataProductType.Correlator_data = DataProductType._CF_enumeration.addEnumeration(unicode_value='Correlator data', tag='Correlator_data')
DataProductType.Beam_Formed_data = DataProductType._CF_enumeration.addEnumeration(unicode_value='Beam Formed data', tag='Beam_Formed_data')
DataProductType.Transient_Buffer_Board_data = DataProductType._CF_enumeration.addEnumeration(unicode_value='Transient Buffer Board data', tag='Transient_Buffer_Board_data')
DataProductType.Sky_Image = DataProductType._CF_enumeration.addEnumeration(unicode_value='Sky Image', tag='Sky_Image')
DataProductType.Pixel_Map = DataProductType._CF_enumeration.addEnumeration(unicode_value='Pixel Map', tag='Pixel_Map')
DataProductType.Direct_Data_Storage_data = DataProductType._CF_enumeration.addEnumeration(unicode_value='Direct Data Storage data', tag='Direct_Data_Storage_data')
DataProductType.Dynamic_Spectra_data = DataProductType._CF_enumeration.addEnumeration(unicode_value='Dynamic Spectra data', tag='Dynamic_Spectra_data')
DataProductType.Instrument_Model = DataProductType._CF_enumeration.addEnumeration(unicode_value='Instrument Model', tag='Instrument_Model')
DataProductType.Sky_Model = DataProductType._CF_enumeration.addEnumeration(unicode_value='Sky Model', tag='Sky_Model')
DataProductType.Pulsar_pipeline_output = DataProductType._CF_enumeration.addEnumeration(unicode_value='Pulsar pipeline output', tag='Pulsar_pipeline_output')
DataProductType.Pulsar_pipeline_summary_output = DataProductType._CF_enumeration.addEnumeration(unicode_value='Pulsar pipeline summary output', tag='Pulsar_pipeline_summary_output')
DataProductType.Non_Standard = DataProductType._CF_enumeration.addEnumeration(unicode_value='Non Standard', tag='Non_Standard')
DataProductType.Unknown = DataProductType._CF_enumeration.addEnumeration(unicode_value='Unknown', tag='Unknown')
DataProductType._InitializeFacetMap(DataProductType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'DataProductType', DataProductType)
_module_typeBindings.DataProductType = DataProductType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}ChecksumAlgorithm
class ChecksumAlgorithm (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ChecksumAlgorithm')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 722, 1)
    _Documentation = None
ChecksumAlgorithm._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ChecksumAlgorithm, enum_prefix=None)
ChecksumAlgorithm.MD5 = ChecksumAlgorithm._CF_enumeration.addEnumeration(unicode_value='MD5', tag='MD5')
ChecksumAlgorithm.Adler32 = ChecksumAlgorithm._CF_enumeration.addEnumeration(unicode_value='Adler32', tag='Adler32')
ChecksumAlgorithm._InitializeFacetMap(ChecksumAlgorithm._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ChecksumAlgorithm', ChecksumAlgorithm)
_module_typeBindings.ChecksumAlgorithm = ChecksumAlgorithm

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}FileFormatType
class FileFormatType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FileFormatType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 742, 1)
    _Documentation = None
FileFormatType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=FileFormatType, enum_prefix=None)
FileFormatType.FITS = FileFormatType._CF_enumeration.addEnumeration(unicode_value='FITS', tag='FITS')
FileFormatType.AIPSCASA = FileFormatType._CF_enumeration.addEnumeration(unicode_value='AIPS++/CASA', tag='AIPSCASA')
FileFormatType.HDF5 = FileFormatType._CF_enumeration.addEnumeration(unicode_value='HDF5', tag='HDF5')
FileFormatType.PULP = FileFormatType._CF_enumeration.addEnumeration(unicode_value='PULP', tag='PULP')
FileFormatType.PREFACTOR = FileFormatType._CF_enumeration.addEnumeration(unicode_value='PREFACTOR', tag='PREFACTOR')
FileFormatType.UNDOCUMENTED = FileFormatType._CF_enumeration.addEnumeration(unicode_value='UNDOCUMENTED', tag='UNDOCUMENTED')
FileFormatType._InitializeFacetMap(FileFormatType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'FileFormatType', FileFormatType)
_module_typeBindings.FileFormatType = FileFormatType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}PolarizationType
class PolarizationType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PolarizationType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 764, 1)
    _Documentation = None
PolarizationType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=PolarizationType, enum_prefix=None)
PolarizationType.None_ = PolarizationType._CF_enumeration.addEnumeration(unicode_value='None', tag='None_')
PolarizationType.I = PolarizationType._CF_enumeration.addEnumeration(unicode_value='I', tag='I')
PolarizationType.Q = PolarizationType._CF_enumeration.addEnumeration(unicode_value='Q', tag='Q')
PolarizationType.U = PolarizationType._CF_enumeration.addEnumeration(unicode_value='U', tag='U')
PolarizationType.V = PolarizationType._CF_enumeration.addEnumeration(unicode_value='V', tag='V')
PolarizationType.RR = PolarizationType._CF_enumeration.addEnumeration(unicode_value='RR', tag='RR')
PolarizationType.RL = PolarizationType._CF_enumeration.addEnumeration(unicode_value='RL', tag='RL')
PolarizationType.LR = PolarizationType._CF_enumeration.addEnumeration(unicode_value='LR', tag='LR')
PolarizationType.LL = PolarizationType._CF_enumeration.addEnumeration(unicode_value='LL', tag='LL')
PolarizationType.XX = PolarizationType._CF_enumeration.addEnumeration(unicode_value='XX', tag='XX')
PolarizationType.XY = PolarizationType._CF_enumeration.addEnumeration(unicode_value='XY', tag='XY')
PolarizationType.YX = PolarizationType._CF_enumeration.addEnumeration(unicode_value='YX', tag='YX')
PolarizationType.YY = PolarizationType._CF_enumeration.addEnumeration(unicode_value='YY', tag='YY')
PolarizationType.Xre = PolarizationType._CF_enumeration.addEnumeration(unicode_value='Xre', tag='Xre')
PolarizationType.Xim = PolarizationType._CF_enumeration.addEnumeration(unicode_value='Xim', tag='Xim')
PolarizationType.Yre = PolarizationType._CF_enumeration.addEnumeration(unicode_value='Yre', tag='Yre')
PolarizationType.Yim = PolarizationType._CF_enumeration.addEnumeration(unicode_value='Yim', tag='Yim')
PolarizationType._InitializeFacetMap(PolarizationType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'PolarizationType', PolarizationType)
_module_typeBindings.PolarizationType = PolarizationType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}PulsarPipelineDataType
class PulsarPipelineDataType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PulsarPipelineDataType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 939, 1)
    _Documentation = None
PulsarPipelineDataType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=PulsarPipelineDataType, enum_prefix=None)
PulsarPipelineDataType.CoherentStokes = PulsarPipelineDataType._CF_enumeration.addEnumeration(unicode_value='CoherentStokes', tag='CoherentStokes')
PulsarPipelineDataType.IncoherentStokes = PulsarPipelineDataType._CF_enumeration.addEnumeration(unicode_value='IncoherentStokes', tag='IncoherentStokes')
PulsarPipelineDataType.ComplexVoltages = PulsarPipelineDataType._CF_enumeration.addEnumeration(unicode_value='ComplexVoltages', tag='ComplexVoltages')
PulsarPipelineDataType.SummaryCoherentStokes = PulsarPipelineDataType._CF_enumeration.addEnumeration(unicode_value='SummaryCoherentStokes', tag='SummaryCoherentStokes')
PulsarPipelineDataType.SummaryIncoherentStokes = PulsarPipelineDataType._CF_enumeration.addEnumeration(unicode_value='SummaryIncoherentStokes', tag='SummaryIncoherentStokes')
PulsarPipelineDataType.SummaryComplexVoltages = PulsarPipelineDataType._CF_enumeration.addEnumeration(unicode_value='SummaryComplexVoltages', tag='SummaryComplexVoltages')
PulsarPipelineDataType._InitializeFacetMap(PulsarPipelineDataType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'PulsarPipelineDataType', PulsarPipelineDataType)
_module_typeBindings.PulsarPipelineDataType = PulsarPipelineDataType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}RaDecSystem
class RaDecSystem (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RaDecSystem')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1023, 1)
    _Documentation = None
RaDecSystem._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=RaDecSystem, enum_prefix=None)
RaDecSystem.ICRS = RaDecSystem._CF_enumeration.addEnumeration(unicode_value='ICRS', tag='ICRS')
RaDecSystem.FK5 = RaDecSystem._CF_enumeration.addEnumeration(unicode_value='FK5', tag='FK5')
RaDecSystem.FK4 = RaDecSystem._CF_enumeration.addEnumeration(unicode_value='FK4', tag='FK4')
RaDecSystem.FK4_NO_E = RaDecSystem._CF_enumeration.addEnumeration(unicode_value='FK4-NO-E', tag='FK4_NO_E')
RaDecSystem.GAPPT = RaDecSystem._CF_enumeration.addEnumeration(unicode_value='GAPPT', tag='GAPPT')
RaDecSystem._InitializeFacetMap(RaDecSystem._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'RaDecSystem', RaDecSystem)
_module_typeBindings.RaDecSystem = RaDecSystem

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}LocationFrame
class LocationFrame (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LocationFrame')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1032, 1)
    _Documentation = None
LocationFrame._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=LocationFrame, enum_prefix=None)
LocationFrame.GEOCENTER = LocationFrame._CF_enumeration.addEnumeration(unicode_value='GEOCENTER', tag='GEOCENTER')
LocationFrame.BARYCENTER = LocationFrame._CF_enumeration.addEnumeration(unicode_value='BARYCENTER', tag='BARYCENTER')
LocationFrame.HELIOCENTER = LocationFrame._CF_enumeration.addEnumeration(unicode_value='HELIOCENTER', tag='HELIOCENTER')
LocationFrame.TOPOCENTER = LocationFrame._CF_enumeration.addEnumeration(unicode_value='TOPOCENTER', tag='TOPOCENTER')
LocationFrame.LSRK = LocationFrame._CF_enumeration.addEnumeration(unicode_value='LSRK', tag='LSRK')
LocationFrame.LSRD = LocationFrame._CF_enumeration.addEnumeration(unicode_value='LSRD', tag='LSRD')
LocationFrame.GALACTIC = LocationFrame._CF_enumeration.addEnumeration(unicode_value='GALACTIC', tag='GALACTIC')
LocationFrame.LOCAL_GROUP = LocationFrame._CF_enumeration.addEnumeration(unicode_value='LOCAL_GROUP', tag='LOCAL_GROUP')
LocationFrame.RELOCATABLE = LocationFrame._CF_enumeration.addEnumeration(unicode_value='RELOCATABLE', tag='RELOCATABLE')
LocationFrame._InitializeFacetMap(LocationFrame._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'LocationFrame', LocationFrame)
_module_typeBindings.LocationFrame = LocationFrame

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}SpectralQuantityType
class SpectralQuantityType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SpectralQuantityType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1067, 1)
    _Documentation = None
SpectralQuantityType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=SpectralQuantityType, enum_prefix=None)
SpectralQuantityType.Frequency = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='Frequency', tag='Frequency')
SpectralQuantityType.Energy = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='Energy', tag='Energy')
SpectralQuantityType.Wavenumber = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='Wavenumber', tag='Wavenumber')
SpectralQuantityType.VelocityRadio = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='VelocityRadio', tag='VelocityRadio')
SpectralQuantityType.VelocityOptical = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='VelocityOptical', tag='VelocityOptical')
SpectralQuantityType.VelocityAppRadial = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='VelocityAppRadial', tag='VelocityAppRadial')
SpectralQuantityType.Redshift = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='Redshift', tag='Redshift')
SpectralQuantityType.WaveLengthVacuum = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='WaveLengthVacuum', tag='WaveLengthVacuum')
SpectralQuantityType.WaveLengthAir = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='WaveLengthAir', tag='WaveLengthAir')
SpectralQuantityType.BetaFactor = SpectralQuantityType._CF_enumeration.addEnumeration(unicode_value='BetaFactor', tag='BetaFactor')
SpectralQuantityType._InitializeFacetMap(SpectralQuantityType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'SpectralQuantityType', SpectralQuantityType)
_module_typeBindings.SpectralQuantityType = SpectralQuantityType

# Atomic simple type: {http://www.astron.nl/SIP-Lofar}Telescope
class Telescope (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Telescope')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1180, 1)
    _Documentation = None
Telescope._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=Telescope, enum_prefix=None)
Telescope.LOFAR = Telescope._CF_enumeration.addEnumeration(unicode_value='LOFAR', tag='LOFAR')
Telescope._InitializeFacetMap(Telescope._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'Telescope', Telescope)
_module_typeBindings.Telescope = Telescope

# Complex type {http://www.astron.nl/SIP-Lofar}ListOfFrequencies with content type ELEMENT_ONLY
class ListOfFrequencies (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}ListOfFrequencies with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ListOfFrequencies')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 102, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element frequencies uses Python identifier frequencies
    __frequencies = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'frequencies'), 'frequencies', '__httpwww_astron_nlSIP_Lofar_ListOfFrequencies_frequencies', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 104, 3), )

    
    frequencies = property(__frequencies.value, __frequencies.set, None, None)

    
    # Element unit uses Python identifier unit
    __unit = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'unit'), 'unit', '__httpwww_astron_nlSIP_Lofar_ListOfFrequencies_unit', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 105, 3), )

    
    unit = property(__unit.value, __unit.set, None, None)

    _ElementMap.update({
        __frequencies.name() : __frequencies,
        __unit.name() : __unit
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ListOfFrequencies = ListOfFrequencies
Namespace.addCategoryObject('typeBinding', 'ListOfFrequencies', ListOfFrequencies)


# Complex type {http://www.astron.nl/SIP-Lofar}IdentifierType with content type ELEMENT_ONLY
class IdentifierType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}IdentifierType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'IdentifierType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 112, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element source uses Python identifier source
    __source = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'source'), 'source', '__httpwww_astron_nlSIP_Lofar_IdentifierType_source', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 114, 3), )

    
    source = property(__source.value, __source.set, None, None)

    
    # Element identifier uses Python identifier identifier
    __identifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'identifier'), 'identifier', '__httpwww_astron_nlSIP_Lofar_IdentifierType_identifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 115, 3), )

    
    identifier = property(__identifier.value, __identifier.set, None, None)

    
    # Element name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__httpwww_astron_nlSIP_Lofar_IdentifierType_name', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 116, 3), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element label uses Python identifier label
    __label = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'label'), 'label', '__httpwww_astron_nlSIP_Lofar_IdentifierType_label', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 117, 12), )

    
    label = property(__label.value, __label.set, None, None)

    _ElementMap.update({
        __source.name() : __source,
        __identifier.name() : __identifier,
        __name.name() : __name,
        __label.name() : __label
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.IdentifierType = IdentifierType
Namespace.addCategoryObject('typeBinding', 'IdentifierType', IdentifierType)


# Complex type {http://www.astron.nl/SIP-Lofar}Pointing with content type ELEMENT_ONLY
class Pointing (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Pointing with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Pointing')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 131, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element rightAscension uses Python identifier rightAscension
    __rightAscension = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'rightAscension'), 'rightAscension', '__httpwww_astron_nlSIP_Lofar_Pointing_rightAscension', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 134, 4), )

    
    rightAscension = property(__rightAscension.value, __rightAscension.set, None, None)

    
    # Element azimuth uses Python identifier azimuth
    __azimuth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'azimuth'), 'azimuth', '__httpwww_astron_nlSIP_Lofar_Pointing_azimuth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 135, 4), )

    
    azimuth = property(__azimuth.value, __azimuth.set, None, None)

    
    # Element declination uses Python identifier declination
    __declination = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'declination'), 'declination', '__httpwww_astron_nlSIP_Lofar_Pointing_declination', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 138, 4), )

    
    declination = property(__declination.value, __declination.set, None, None)

    
    # Element altitude uses Python identifier altitude
    __altitude = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'altitude'), 'altitude', '__httpwww_astron_nlSIP_Lofar_Pointing_altitude', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 139, 4), )

    
    altitude = property(__altitude.value, __altitude.set, None, None)

    
    # Element equinox uses Python identifier equinox
    __equinox = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'equinox'), 'equinox', '__httpwww_astron_nlSIP_Lofar_Pointing_equinox', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 141, 3), )

    
    equinox = property(__equinox.value, __equinox.set, None, None)

    _ElementMap.update({
        __rightAscension.name() : __rightAscension,
        __azimuth.name() : __azimuth,
        __declination.name() : __declination,
        __altitude.name() : __altitude,
        __equinox.name() : __equinox
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Pointing = Pointing
Namespace.addCategoryObject('typeBinding', 'Pointing', Pointing)


# Complex type {http://www.astron.nl/SIP-Lofar}Coordinates with content type ELEMENT_ONLY
class Coordinates (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Coordinates with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Coordinates')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 155, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element coordinateSystem uses Python identifier coordinateSystem
    __coordinateSystem = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'coordinateSystem'), 'coordinateSystem', '__httpwww_astron_nlSIP_Lofar_Coordinates_coordinateSystem', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 157, 3), )

    
    coordinateSystem = property(__coordinateSystem.value, __coordinateSystem.set, None, None)

    
    # Element x uses Python identifier x
    __x = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'x'), 'x', '__httpwww_astron_nlSIP_Lofar_Coordinates_x', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 168, 5), )

    
    x = property(__x.value, __x.set, None, None)

    
    # Element y uses Python identifier y
    __y = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'y'), 'y', '__httpwww_astron_nlSIP_Lofar_Coordinates_y', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 169, 5), )

    
    y = property(__y.value, __y.set, None, None)

    
    # Element z uses Python identifier z
    __z = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'z'), 'z', '__httpwww_astron_nlSIP_Lofar_Coordinates_z', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 170, 5), )

    
    z = property(__z.value, __z.set, None, None)

    
    # Element radius uses Python identifier radius
    __radius = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'radius'), 'radius', '__httpwww_astron_nlSIP_Lofar_Coordinates_radius', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 173, 5), )

    
    radius = property(__radius.value, __radius.set, None, None)

    
    # Element longitude uses Python identifier longitude
    __longitude = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'longitude'), 'longitude', '__httpwww_astron_nlSIP_Lofar_Coordinates_longitude', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 174, 5), )

    
    longitude = property(__longitude.value, __longitude.set, None, None)

    
    # Element latitude uses Python identifier latitude
    __latitude = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'latitude'), 'latitude', '__httpwww_astron_nlSIP_Lofar_Coordinates_latitude', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 175, 5), )

    
    latitude = property(__latitude.value, __latitude.set, None, None)

    _ElementMap.update({
        __coordinateSystem.name() : __coordinateSystem,
        __x.name() : __x,
        __y.name() : __y,
        __z.name() : __z,
        __radius.name() : __radius,
        __longitude.name() : __longitude,
        __latitude.name() : __latitude
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Coordinates = Coordinates
Namespace.addCategoryObject('typeBinding', 'Coordinates', Coordinates)


# Complex type {http://www.astron.nl/SIP-Lofar}AntennaField with content type ELEMENT_ONLY
class AntennaField (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}AntennaField with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AntennaField')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 204, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__httpwww_astron_nlSIP_Lofar_AntennaField_name', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 206, 3), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element location uses Python identifier location
    __location = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'location'), 'location', '__httpwww_astron_nlSIP_Lofar_AntennaField_location', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 207, 3), )

    
    location = property(__location.value, __location.set, None, None)

    _ElementMap.update({
        __name.name() : __name,
        __location.name() : __location
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.AntennaField = AntennaField
Namespace.addCategoryObject('typeBinding', 'AntennaField', AntennaField)


# Complex type {http://www.astron.nl/SIP-Lofar}Stations with content type ELEMENT_ONLY
class Stations (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Stations with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Stations')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 210, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element station uses Python identifier station
    __station = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'station'), 'station', '__httpwww_astron_nlSIP_Lofar_Stations_station', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 212, 3), )

    
    station = property(__station.value, __station.set, None, None)

    _ElementMap.update({
        __station.name() : __station
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Stations = Stations
Namespace.addCategoryObject('typeBinding', 'Stations', Stations)


# Complex type {http://www.astron.nl/SIP-Lofar}Station with content type ELEMENT_ONLY
class Station (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Station with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Station')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 218, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__httpwww_astron_nlSIP_Lofar_Station_name', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 220, 3), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element stationType uses Python identifier stationType
    __stationType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stationType'), 'stationType', '__httpwww_astron_nlSIP_Lofar_Station_stationType', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 221, 3), )

    
    stationType = property(__stationType.value, __stationType.set, None, None)

    
    # Element antennaField uses Python identifier antennaField
    __antennaField = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'antennaField'), 'antennaField', '__httpwww_astron_nlSIP_Lofar_Station_antennaField', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 222, 3), )

    
    antennaField = property(__antennaField.value, __antennaField.set, None, None)

    _ElementMap.update({
        __name.name() : __name,
        __stationType.name() : __stationType,
        __antennaField.name() : __antennaField
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Station = Station
Namespace.addCategoryObject('typeBinding', 'Station', Station)


# Complex type {http://www.astron.nl/SIP-Lofar}ProcessRelation with content type ELEMENT_ONLY
class ProcessRelation (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}ProcessRelation with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ProcessRelation')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 244, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element relationType uses Python identifier relationType
    __relationType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'relationType'), 'relationType', '__httpwww_astron_nlSIP_Lofar_ProcessRelation_relationType', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 246, 3), )

    
    relationType = property(__relationType.value, __relationType.set, None, None)

    
    # Element identifier uses Python identifier identifier
    __identifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'identifier'), 'identifier', '__httpwww_astron_nlSIP_Lofar_ProcessRelation_identifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 247, 3), )

    
    identifier = property(__identifier.value, __identifier.set, None, None)

    
    # Element name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__httpwww_astron_nlSIP_Lofar_ProcessRelation_name', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 248, 3), )

    
    name = property(__name.value, __name.set, None, None)

    _ElementMap.update({
        __relationType.name() : __relationType,
        __identifier.name() : __identifier,
        __name.name() : __name
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ProcessRelation = ProcessRelation
Namespace.addCategoryObject('typeBinding', 'ProcessRelation', ProcessRelation)


# Complex type {http://www.astron.nl/SIP-Lofar}ProcessRelations with content type ELEMENT_ONLY
class ProcessRelations (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}ProcessRelations with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ProcessRelations')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 251, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element relation uses Python identifier relation
    __relation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'relation'), 'relation', '__httpwww_astron_nlSIP_Lofar_ProcessRelations_relation', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 253, 3), )

    
    relation = property(__relation.value, __relation.set, None, None)

    _ElementMap.update({
        __relation.name() : __relation
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ProcessRelations = ProcessRelations
Namespace.addCategoryObject('typeBinding', 'ProcessRelations', ProcessRelations)


# Complex type {http://www.astron.nl/SIP-Lofar}Process with content type ELEMENT_ONLY
class Process (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Process with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Process')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 256, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element processIdentifier uses Python identifier processIdentifier
    __processIdentifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'processIdentifier'), 'processIdentifier', '__httpwww_astron_nlSIP_Lofar_Process_processIdentifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3), )

    
    processIdentifier = property(__processIdentifier.value, __processIdentifier.set, None, None)

    
    # Element observationId uses Python identifier observationId
    __observationId = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observationId'), 'observationId', '__httpwww_astron_nlSIP_Lofar_Process_observationId', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3), )

    
    observationId = property(__observationId.value, __observationId.set, None, None)

    
    # Element parset uses Python identifier parset
    __parset = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'parset'), 'parset', '__httpwww_astron_nlSIP_Lofar_Process_parset', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3), )

    
    parset = property(__parset.value, __parset.set, None, None)

    
    # Element strategyName uses Python identifier strategyName
    __strategyName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'strategyName'), 'strategyName', '__httpwww_astron_nlSIP_Lofar_Process_strategyName', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3), )

    
    strategyName = property(__strategyName.value, __strategyName.set, None, None)

    
    # Element strategyDescription uses Python identifier strategyDescription
    __strategyDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'strategyDescription'), 'strategyDescription', '__httpwww_astron_nlSIP_Lofar_Process_strategyDescription', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3), )

    
    strategyDescription = property(__strategyDescription.value, __strategyDescription.set, None, None)

    
    # Element startTime uses Python identifier startTime
    __startTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'startTime'), 'startTime', '__httpwww_astron_nlSIP_Lofar_Process_startTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3), )

    
    startTime = property(__startTime.value, __startTime.set, None, None)

    
    # Element duration uses Python identifier duration
    __duration = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'duration'), 'duration', '__httpwww_astron_nlSIP_Lofar_Process_duration', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3), )

    
    duration = property(__duration.value, __duration.set, None, None)

    
    # Element relations uses Python identifier relations
    __relations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'relations'), 'relations', '__httpwww_astron_nlSIP_Lofar_Process_relations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3), )

    
    relations = property(__relations.value, __relations.set, None, None)

    _ElementMap.update({
        __processIdentifier.name() : __processIdentifier,
        __observationId.name() : __observationId,
        __parset.name() : __parset,
        __strategyName.name() : __strategyName,
        __strategyDescription.name() : __strategyDescription,
        __startTime.name() : __startTime,
        __duration.name() : __duration,
        __relations.name() : __relations
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Process = Process
Namespace.addCategoryObject('typeBinding', 'Process', Process)


# Complex type {http://www.astron.nl/SIP-Lofar}Processing with content type ELEMENT_ONLY
class Processing (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Processing with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Processing')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 439, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element correlator uses Python identifier correlator
    __correlator = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'correlator'), 'correlator', '__httpwww_astron_nlSIP_Lofar_Processing_correlator', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 441, 3), )

    
    correlator = property(__correlator.value, __correlator.set, None, None)

    
    # Element coherentStokes uses Python identifier coherentStokes
    __coherentStokes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'coherentStokes'), 'coherentStokes', '__httpwww_astron_nlSIP_Lofar_Processing_coherentStokes', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 442, 3), )

    
    coherentStokes = property(__coherentStokes.value, __coherentStokes.set, None, None)

    
    # Element incoherentStokes uses Python identifier incoherentStokes
    __incoherentStokes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'incoherentStokes'), 'incoherentStokes', '__httpwww_astron_nlSIP_Lofar_Processing_incoherentStokes', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 443, 3), )

    
    incoherentStokes = property(__incoherentStokes.value, __incoherentStokes.set, None, None)

    
    # Element flysEye uses Python identifier flysEye
    __flysEye = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'flysEye'), 'flysEye', '__httpwww_astron_nlSIP_Lofar_Processing_flysEye', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 444, 3), )

    
    flysEye = property(__flysEye.value, __flysEye.set, None, None)

    
    # Element nonStandard uses Python identifier nonStandard
    __nonStandard = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'nonStandard'), 'nonStandard', '__httpwww_astron_nlSIP_Lofar_Processing_nonStandard', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 445, 3), )

    
    nonStandard = property(__nonStandard.value, __nonStandard.set, None, None)

    _ElementMap.update({
        __correlator.name() : __correlator,
        __coherentStokes.name() : __coherentStokes,
        __incoherentStokes.name() : __incoherentStokes,
        __flysEye.name() : __flysEye,
        __nonStandard.name() : __nonStandard
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Processing = Processing
Namespace.addCategoryObject('typeBinding', 'Processing', Processing)


# Complex type {http://www.astron.nl/SIP-Lofar}RealTimeProcess with content type ELEMENT_ONLY
class RealTimeProcess (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}RealTimeProcess with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RealTimeProcess')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 448, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element processingType uses Python identifier processingType
    __processingType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'processingType'), 'processingType', '__httpwww_astron_nlSIP_Lofar_RealTimeProcess_processingType', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3), )

    
    processingType = property(__processingType.value, __processingType.set, None, None)

    _ElementMap.update({
        __processingType.name() : __processingType
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.RealTimeProcess = RealTimeProcess
Namespace.addCategoryObject('typeBinding', 'RealTimeProcess', RealTimeProcess)


# Complex type {http://www.astron.nl/SIP-Lofar}TransientBufferBoardEvents with content type ELEMENT_ONLY
class TransientBufferBoardEvents (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}TransientBufferBoardEvents with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TransientBufferBoardEvents')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 534, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element transientBufferBoardEvent uses Python identifier transientBufferBoardEvent
    __transientBufferBoardEvent = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'transientBufferBoardEvent'), 'transientBufferBoardEvent', '__httpwww_astron_nlSIP_Lofar_TransientBufferBoardEvents_transientBufferBoardEvent', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 536, 3), )

    
    transientBufferBoardEvent = property(__transientBufferBoardEvent.value, __transientBufferBoardEvent.set, None, None)

    _ElementMap.update({
        __transientBufferBoardEvent.name() : __transientBufferBoardEvent
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.TransientBufferBoardEvents = TransientBufferBoardEvents
Namespace.addCategoryObject('typeBinding', 'TransientBufferBoardEvents', TransientBufferBoardEvents)


# Complex type {http://www.astron.nl/SIP-Lofar}TransientBufferBoardEvent with content type ELEMENT_ONLY
class TransientBufferBoardEvent (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}TransientBufferBoardEvent with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TransientBufferBoardEvent')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 539, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element eventSource uses Python identifier eventSource
    __eventSource = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'eventSource'), 'eventSource', '__httpwww_astron_nlSIP_Lofar_TransientBufferBoardEvent_eventSource', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 541, 3), )

    
    eventSource = property(__eventSource.value, __eventSource.set, None, None)

    _ElementMap.update({
        __eventSource.name() : __eventSource
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.TransientBufferBoardEvent = TransientBufferBoardEvent
Namespace.addCategoryObject('typeBinding', 'TransientBufferBoardEvent', TransientBufferBoardEvent)


# Complex type {http://www.astron.nl/SIP-Lofar}SubArrayPointings with content type ELEMENT_ONLY
class SubArrayPointings (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}SubArrayPointings with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SubArrayPointings')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 544, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element subArrayPointing uses Python identifier subArrayPointing
    __subArrayPointing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subArrayPointing'), 'subArrayPointing', '__httpwww_astron_nlSIP_Lofar_SubArrayPointings_subArrayPointing', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 546, 3), )

    
    subArrayPointing = property(__subArrayPointing.value, __subArrayPointing.set, None, None)

    _ElementMap.update({
        __subArrayPointing.name() : __subArrayPointing
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.SubArrayPointings = SubArrayPointings
Namespace.addCategoryObject('typeBinding', 'SubArrayPointings', SubArrayPointings)


# Complex type {http://www.astron.nl/SIP-Lofar}SubArrayPointing with content type ELEMENT_ONLY
class SubArrayPointing (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}SubArrayPointing with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SubArrayPointing')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 557, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element pointing uses Python identifier pointing
    __pointing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'pointing'), 'pointing', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_pointing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 559, 3), )

    
    pointing = property(__pointing.value, __pointing.set, None, None)

    
    # Element beamNumber uses Python identifier beamNumber
    __beamNumber = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'beamNumber'), 'beamNumber', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_beamNumber', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 560, 3), )

    
    beamNumber = property(__beamNumber.value, __beamNumber.set, None, None)

    
    # Element measurementDescription uses Python identifier measurementDescription
    __measurementDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'measurementDescription'), 'measurementDescription', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_measurementDescription', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 561, 3), )

    
    measurementDescription = property(__measurementDescription.value, __measurementDescription.set, None, None)

    
    # Element subArrayPointingIdentifier uses Python identifier subArrayPointingIdentifier
    __subArrayPointingIdentifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier'), 'subArrayPointingIdentifier', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_subArrayPointingIdentifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 562, 3), )

    
    subArrayPointingIdentifier = property(__subArrayPointingIdentifier.value, __subArrayPointingIdentifier.set, None, None)

    
    # Element measurementType uses Python identifier measurementType
    __measurementType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'measurementType'), 'measurementType', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_measurementType', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 563, 3), )

    
    measurementType = property(__measurementType.value, __measurementType.set, None, None)

    
    # Element targetName uses Python identifier targetName
    __targetName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'targetName'), 'targetName', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_targetName', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 564, 3), )

    
    targetName = property(__targetName.value, __targetName.set, None, None)

    
    # Element startTime uses Python identifier startTime
    __startTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'startTime'), 'startTime', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_startTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 565, 3), )

    
    startTime = property(__startTime.value, __startTime.set, None, None)

    
    # Element duration uses Python identifier duration
    __duration = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'duration'), 'duration', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_duration', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 566, 3), )

    
    duration = property(__duration.value, __duration.set, None, None)

    
    # Element numberOfProcessing uses Python identifier numberOfProcessing
    __numberOfProcessing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfProcessing'), 'numberOfProcessing', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_numberOfProcessing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 567, 3), )

    
    numberOfProcessing = property(__numberOfProcessing.value, __numberOfProcessing.set, None, None)

    
    # Element processing uses Python identifier processing
    __processing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'processing'), 'processing', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_processing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 568, 3), )

    
    processing = property(__processing.value, __processing.set, None, None)

    
    # Element numberOfCorrelatedDataProducts uses Python identifier numberOfCorrelatedDataProducts
    __numberOfCorrelatedDataProducts = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), 'numberOfCorrelatedDataProducts', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_numberOfCorrelatedDataProducts', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 569, 3), )

    
    numberOfCorrelatedDataProducts = property(__numberOfCorrelatedDataProducts.value, __numberOfCorrelatedDataProducts.set, None, None)

    
    # Element numberOfBeamFormedDataProducts uses Python identifier numberOfBeamFormedDataProducts
    __numberOfBeamFormedDataProducts = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfBeamFormedDataProducts'), 'numberOfBeamFormedDataProducts', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_numberOfBeamFormedDataProducts', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 570, 3), )

    
    numberOfBeamFormedDataProducts = property(__numberOfBeamFormedDataProducts.value, __numberOfBeamFormedDataProducts.set, None, None)

    
    # Element relations uses Python identifier relations
    __relations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'relations'), 'relations', '__httpwww_astron_nlSIP_Lofar_SubArrayPointing_relations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 571, 3), )

    
    relations = property(__relations.value, __relations.set, None, None)

    _ElementMap.update({
        __pointing.name() : __pointing,
        __beamNumber.name() : __beamNumber,
        __measurementDescription.name() : __measurementDescription,
        __subArrayPointingIdentifier.name() : __subArrayPointingIdentifier,
        __measurementType.name() : __measurementType,
        __targetName.name() : __targetName,
        __startTime.name() : __startTime,
        __duration.name() : __duration,
        __numberOfProcessing.name() : __numberOfProcessing,
        __processing.name() : __processing,
        __numberOfCorrelatedDataProducts.name() : __numberOfCorrelatedDataProducts,
        __numberOfBeamFormedDataProducts.name() : __numberOfBeamFormedDataProducts,
        __relations.name() : __relations
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.SubArrayPointing = SubArrayPointing
Namespace.addCategoryObject('typeBinding', 'SubArrayPointing', SubArrayPointing)


# Complex type {http://www.astron.nl/SIP-Lofar}DataSources with content type ELEMENT_ONLY
class DataSources (pyxb.binding.basis.complexTypeDefinition):
    """============================Pipeline============================
	
			This section describes the various pipelines.
			"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DataSources')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 574, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element dataProductIdentifier uses Python identifier dataProductIdentifier
    __dataProductIdentifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier'), 'dataProductIdentifier', '__httpwww_astron_nlSIP_Lofar_DataSources_dataProductIdentifier', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 582, 3), )

    
    dataProductIdentifier = property(__dataProductIdentifier.value, __dataProductIdentifier.set, None, None)

    _ElementMap.update({
        __dataProductIdentifier.name() : __dataProductIdentifier
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.DataSources = DataSources
Namespace.addCategoryObject('typeBinding', 'DataSources', DataSources)


# Complex type {http://www.astron.nl/SIP-Lofar}ChecksumType with content type ELEMENT_ONLY
class ChecksumType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}ChecksumType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ChecksumType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 728, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element algorithm uses Python identifier algorithm
    __algorithm = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'algorithm'), 'algorithm', '__httpwww_astron_nlSIP_Lofar_ChecksumType_algorithm', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 730, 3), )

    
    algorithm = property(__algorithm.value, __algorithm.set, None, None)

    
    # Element value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'value'), 'value_', '__httpwww_astron_nlSIP_Lofar_ChecksumType_value', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 731, 3), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __algorithm.name() : __algorithm,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ChecksumType = ChecksumType
Namespace.addCategoryObject('typeBinding', 'ChecksumType', ChecksumType)


# Complex type {http://www.astron.nl/SIP-Lofar}TBBTrigger with content type ELEMENT_ONLY
class TBBTrigger (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}TBBTrigger with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TBBTrigger')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 755, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element type uses Python identifier type
    __type = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpwww_astron_nlSIP_Lofar_TBBTrigger_type', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 757, 3), )

    
    type = property(__type.value, __type.set, None, None)

    
    # Element value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'value'), 'value_', '__httpwww_astron_nlSIP_Lofar_TBBTrigger_value', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 758, 3), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __type.name() : __type,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.TBBTrigger = TBBTrigger
Namespace.addCategoryObject('typeBinding', 'TBBTrigger', TBBTrigger)


# Complex type {http://www.astron.nl/SIP-Lofar}DataProduct with content type ELEMENT_ONLY
class DataProduct (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}DataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 788, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element dataProductType uses Python identifier dataProductType
    __dataProductType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'dataProductType'), 'dataProductType', '__httpwww_astron_nlSIP_Lofar_DataProduct_dataProductType', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3), )

    
    dataProductType = property(__dataProductType.value, __dataProductType.set, None, None)

    
    # Element dataProductIdentifier uses Python identifier dataProductIdentifier
    __dataProductIdentifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier'), 'dataProductIdentifier', '__httpwww_astron_nlSIP_Lofar_DataProduct_dataProductIdentifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3), )

    
    dataProductIdentifier = property(__dataProductIdentifier.value, __dataProductIdentifier.set, None, None)

    
    # Element storageTicket uses Python identifier storageTicket
    __storageTicket = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'storageTicket'), 'storageTicket', '__httpwww_astron_nlSIP_Lofar_DataProduct_storageTicket', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3), )

    
    storageTicket = property(__storageTicket.value, __storageTicket.set, None, None)

    
    # Element size uses Python identifier size
    __size = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'size'), 'size', '__httpwww_astron_nlSIP_Lofar_DataProduct_size', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3), )

    
    size = property(__size.value, __size.set, None, None)

    
    # Element checksum uses Python identifier checksum
    __checksum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'checksum'), 'checksum', '__httpwww_astron_nlSIP_Lofar_DataProduct_checksum', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3), )

    
    checksum = property(__checksum.value, __checksum.set, None, None)

    
    # Element fileName uses Python identifier fileName
    __fileName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'fileName'), 'fileName', '__httpwww_astron_nlSIP_Lofar_DataProduct_fileName', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3), )

    
    fileName = property(__fileName.value, __fileName.set, None, None)

    
    # Element fileFormat uses Python identifier fileFormat
    __fileFormat = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'fileFormat'), 'fileFormat', '__httpwww_astron_nlSIP_Lofar_DataProduct_fileFormat', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3), )

    
    fileFormat = property(__fileFormat.value, __fileFormat.set, None, None)

    
    # Element processIdentifier uses Python identifier processIdentifier
    __processIdentifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'processIdentifier'), 'processIdentifier', '__httpwww_astron_nlSIP_Lofar_DataProduct_processIdentifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3), )

    
    processIdentifier = property(__processIdentifier.value, __processIdentifier.set, None, None)

    _ElementMap.update({
        __dataProductType.name() : __dataProductType,
        __dataProductIdentifier.name() : __dataProductIdentifier,
        __storageTicket.name() : __storageTicket,
        __size.name() : __size,
        __checksum.name() : __checksum,
        __fileName.name() : __fileName,
        __fileFormat.name() : __fileFormat,
        __processIdentifier.name() : __processIdentifier
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.DataProduct = DataProduct
Namespace.addCategoryObject('typeBinding', 'DataProduct', DataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}ArrayBeams with content type ELEMENT_ONLY
class ArrayBeams (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}ArrayBeams with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ArrayBeams')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 869, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element arrayBeam uses Python identifier arrayBeam
    __arrayBeam = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'arrayBeam'), 'arrayBeam', '__httpwww_astron_nlSIP_Lofar_ArrayBeams_arrayBeam', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 871, 3), )

    
    arrayBeam = property(__arrayBeam.value, __arrayBeam.set, None, None)

    _ElementMap.update({
        __arrayBeam.name() : __arrayBeam
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ArrayBeams = ArrayBeams
Namespace.addCategoryObject('typeBinding', 'ArrayBeams', ArrayBeams)


# Complex type {http://www.astron.nl/SIP-Lofar}ArrayBeam with content type ELEMENT_ONLY
class ArrayBeam (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}ArrayBeam with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ArrayBeam')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 877, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element subArrayPointingIdentifier uses Python identifier subArrayPointingIdentifier
    __subArrayPointingIdentifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier'), 'subArrayPointingIdentifier', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_subArrayPointingIdentifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 879, 3), )

    
    subArrayPointingIdentifier = property(__subArrayPointingIdentifier.value, __subArrayPointingIdentifier.set, None, None)

    
    # Element beamNumber uses Python identifier beamNumber
    __beamNumber = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'beamNumber'), 'beamNumber', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_beamNumber', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 880, 3), )

    
    beamNumber = property(__beamNumber.value, __beamNumber.set, None, None)

    
    # Element dispersionMeasure uses Python identifier dispersionMeasure
    __dispersionMeasure = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'dispersionMeasure'), 'dispersionMeasure', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_dispersionMeasure', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 881, 3), )

    
    dispersionMeasure = property(__dispersionMeasure.value, __dispersionMeasure.set, None, None)

    
    # Element numberOfSubbands uses Python identifier numberOfSubbands
    __numberOfSubbands = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfSubbands'), 'numberOfSubbands', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_numberOfSubbands', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 882, 3), )

    
    numberOfSubbands = property(__numberOfSubbands.value, __numberOfSubbands.set, None, None)

    
    # Element stationSubbands uses Python identifier stationSubbands
    __stationSubbands = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stationSubbands'), 'stationSubbands', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_stationSubbands', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 883, 3), )

    
    stationSubbands = property(__stationSubbands.value, __stationSubbands.set, None, None)

    
    # Element samplingTime uses Python identifier samplingTime
    __samplingTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'samplingTime'), 'samplingTime', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_samplingTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 884, 3), )

    
    samplingTime = property(__samplingTime.value, __samplingTime.set, None, None)

    
    # Element centralFrequencies uses Python identifier centralFrequencies
    __centralFrequencies = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'centralFrequencies'), 'centralFrequencies', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_centralFrequencies', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 885, 3), )

    
    centralFrequencies = property(__centralFrequencies.value, __centralFrequencies.set, None, None)

    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 886, 3), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 887, 3), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    
    # Element stokes uses Python identifier stokes
    __stokes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stokes'), 'stokes', '__httpwww_astron_nlSIP_Lofar_ArrayBeam_stokes', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3), )

    
    stokes = property(__stokes.value, __stokes.set, None, None)

    _ElementMap.update({
        __subArrayPointingIdentifier.name() : __subArrayPointingIdentifier,
        __beamNumber.name() : __beamNumber,
        __dispersionMeasure.name() : __dispersionMeasure,
        __numberOfSubbands.name() : __numberOfSubbands,
        __stationSubbands.name() : __stationSubbands,
        __samplingTime.name() : __samplingTime,
        __centralFrequencies.name() : __centralFrequencies,
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband,
        __stokes.name() : __stokes
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ArrayBeam = ArrayBeam
Namespace.addCategoryObject('typeBinding', 'ArrayBeam', ArrayBeam)


# Complex type {http://www.astron.nl/SIP-Lofar}Axis with content type ELEMENT_ONLY
class Axis (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Axis with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Axis')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 994, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element number uses Python identifier number
    __number = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'number'), 'number', '__httpwww_astron_nlSIP_Lofar_Axis_number', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 996, 3), )

    
    number = property(__number.value, __number.set, None, None)

    
    # Element name uses Python identifier name
    __name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__httpwww_astron_nlSIP_Lofar_Axis_name', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 997, 3), )

    
    name = property(__name.value, __name.set, None, None)

    
    # Element units uses Python identifier units
    __units = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'units'), 'units', '__httpwww_astron_nlSIP_Lofar_Axis_units', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 998, 3), )

    
    units = property(__units.value, __units.set, None, None)

    
    # Element length uses Python identifier length
    __length = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'length'), 'length', '__httpwww_astron_nlSIP_Lofar_Axis_length', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 999, 3), )

    
    length = property(__length.value, __length.set, None, None)

    _ElementMap.update({
        __number.name() : __number,
        __name.name() : __name,
        __units.name() : __units,
        __length.name() : __length
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Axis = Axis
Namespace.addCategoryObject('typeBinding', 'Axis', Axis)


# Complex type {http://www.astron.nl/SIP-Lofar}Coordinate with content type EMPTY
class Coordinate (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Coordinate with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Coordinate')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1020, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Coordinate = Coordinate
Namespace.addCategoryObject('typeBinding', 'Coordinate', Coordinate)


# Complex type {http://www.astron.nl/SIP-Lofar}SpectralQuantity with content type ELEMENT_ONLY
class SpectralQuantity (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}SpectralQuantity with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SpectralQuantity')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1081, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element type uses Python identifier type
    __type = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpwww_astron_nlSIP_Lofar_SpectralQuantity_type', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1083, 3), )

    
    type = property(__type.value, __type.set, None, None)

    
    # Element value uses Python identifier value_
    __value = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'value'), 'value_', '__httpwww_astron_nlSIP_Lofar_SpectralQuantity_value', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1084, 3), )

    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        __type.name() : __type,
        __value.name() : __value
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.SpectralQuantity = SpectralQuantity
Namespace.addCategoryObject('typeBinding', 'SpectralQuantity', SpectralQuantity)


# Complex type {http://www.astron.nl/SIP-Lofar}Parset with content type ELEMENT_ONLY
class Parset (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Parset with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Parset')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1168, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element identifier uses Python identifier identifier
    __identifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'identifier'), 'identifier', '__httpwww_astron_nlSIP_Lofar_Parset_identifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1170, 3), )

    
    identifier = property(__identifier.value, __identifier.set, None, None)

    
    # Element contents uses Python identifier contents
    __contents = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'contents'), 'contents', '__httpwww_astron_nlSIP_Lofar_Parset_contents', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1171, 3), )

    
    contents = property(__contents.value, __contents.set, None, None)

    _ElementMap.update({
        __identifier.name() : __identifier,
        __contents.name() : __contents
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Parset = Parset
Namespace.addCategoryObject('typeBinding', 'Parset', Parset)


# Complex type {http://www.astron.nl/SIP-Lofar}Project with content type ELEMENT_ONLY
class Project (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Project with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Project')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1189, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element projectCode uses Python identifier projectCode
    __projectCode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'projectCode'), 'projectCode', '__httpwww_astron_nlSIP_Lofar_Project_projectCode', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1191, 3), )

    
    projectCode = property(__projectCode.value, __projectCode.set, None, None)

    
    # Element primaryInvestigator uses Python identifier primaryInvestigator
    __primaryInvestigator = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'primaryInvestigator'), 'primaryInvestigator', '__httpwww_astron_nlSIP_Lofar_Project_primaryInvestigator', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1192, 3), )

    
    primaryInvestigator = property(__primaryInvestigator.value, __primaryInvestigator.set, None, None)

    
    # Element coInvestigator uses Python identifier coInvestigator
    __coInvestigator = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'coInvestigator'), 'coInvestigator', '__httpwww_astron_nlSIP_Lofar_Project_coInvestigator', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1193, 3), )

    
    coInvestigator = property(__coInvestigator.value, __coInvestigator.set, None, None)

    
    # Element contactAuthor uses Python identifier contactAuthor
    __contactAuthor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'contactAuthor'), 'contactAuthor', '__httpwww_astron_nlSIP_Lofar_Project_contactAuthor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1194, 3), )

    
    contactAuthor = property(__contactAuthor.value, __contactAuthor.set, None, None)

    
    # Element telescope uses Python identifier telescope
    __telescope = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'telescope'), 'telescope', '__httpwww_astron_nlSIP_Lofar_Project_telescope', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1195, 3), )

    
    telescope = property(__telescope.value, __telescope.set, None, None)

    
    # Element projectDescription uses Python identifier projectDescription
    __projectDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'projectDescription'), 'projectDescription', '__httpwww_astron_nlSIP_Lofar_Project_projectDescription', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1196, 3), )

    
    projectDescription = property(__projectDescription.value, __projectDescription.set, None, None)

    _ElementMap.update({
        __projectCode.name() : __projectCode,
        __primaryInvestigator.name() : __primaryInvestigator,
        __coInvestigator.name() : __coInvestigator,
        __contactAuthor.name() : __contactAuthor,
        __telescope.name() : __telescope,
        __projectDescription.name() : __projectDescription
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Project = Project
Namespace.addCategoryObject('typeBinding', 'Project', Project)


# Complex type {http://www.astron.nl/SIP-Lofar}LTASip with content type ELEMENT_ONLY
class LTASip (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}LTASip with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LTASip')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1207, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element sipGeneratorVersion uses Python identifier sipGeneratorVersion
    __sipGeneratorVersion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'sipGeneratorVersion'), 'sipGeneratorVersion', '__httpwww_astron_nlSIP_Lofar_LTASip_sipGeneratorVersion', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1209, 3), )

    
    sipGeneratorVersion = property(__sipGeneratorVersion.value, __sipGeneratorVersion.set, None, None)

    
    # Element project uses Python identifier project
    __project = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'project'), 'project', '__httpwww_astron_nlSIP_Lofar_LTASip_project', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1210, 3), )

    
    project = property(__project.value, __project.set, None, None)

    
    # Element dataProduct uses Python identifier dataProduct
    __dataProduct = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'dataProduct'), 'dataProduct', '__httpwww_astron_nlSIP_Lofar_LTASip_dataProduct', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1211, 3), )

    
    dataProduct = property(__dataProduct.value, __dataProduct.set, None, None)

    
    # Element observation uses Python identifier observation
    __observation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observation'), 'observation', '__httpwww_astron_nlSIP_Lofar_LTASip_observation', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1212, 3), )

    
    observation = property(__observation.value, __observation.set, None, None)

    
    # Element pipelineRun uses Python identifier pipelineRun
    __pipelineRun = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'pipelineRun'), 'pipelineRun', '__httpwww_astron_nlSIP_Lofar_LTASip_pipelineRun', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1213, 3), )

    
    pipelineRun = property(__pipelineRun.value, __pipelineRun.set, None, None)

    
    # Element unspecifiedProcess uses Python identifier unspecifiedProcess
    __unspecifiedProcess = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'unspecifiedProcess'), 'unspecifiedProcess', '__httpwww_astron_nlSIP_Lofar_LTASip_unspecifiedProcess', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1214, 3), )

    
    unspecifiedProcess = property(__unspecifiedProcess.value, __unspecifiedProcess.set, None, None)

    
    # Element relatedDataProduct uses Python identifier relatedDataProduct
    __relatedDataProduct = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'relatedDataProduct'), 'relatedDataProduct', '__httpwww_astron_nlSIP_Lofar_LTASip_relatedDataProduct', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1215, 3), )

    
    relatedDataProduct = property(__relatedDataProduct.value, __relatedDataProduct.set, None, None)

    
    # Element parset uses Python identifier parset
    __parset = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'parset'), 'parset', '__httpwww_astron_nlSIP_Lofar_LTASip_parset', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1216, 3), )

    
    parset = property(__parset.value, __parset.set, None, None)

    _ElementMap.update({
        __sipGeneratorVersion.name() : __sipGeneratorVersion,
        __project.name() : __project,
        __dataProduct.name() : __dataProduct,
        __observation.name() : __observation,
        __pipelineRun.name() : __pipelineRun,
        __unspecifiedProcess.name() : __unspecifiedProcess,
        __relatedDataProduct.name() : __relatedDataProduct,
        __parset.name() : __parset
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.LTASip = LTASip
Namespace.addCategoryObject('typeBinding', 'LTASip', LTASip)


# Complex type {http://www.astron.nl/SIP-Lofar}Frequency with content type SIMPLE
class Frequency (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Frequency with content type SIMPLE"""
    _TypeDefinition = pyxb.binding.datatypes.double
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Frequency')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 32, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.double
    
    # Attribute units uses Python identifier units
    __units = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'units'), 'units', '__httpwww_astron_nlSIP_Lofar_Frequency_units', _module_typeBindings.FrequencyUnit, required=True)
    __units._DeclarationLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 35, 4)
    __units._UseLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 35, 4)
    
    units = property(__units.value, __units.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __units.name() : __units
    })
_module_typeBindings.Frequency = Frequency
Namespace.addCategoryObject('typeBinding', 'Frequency', Frequency)


# Complex type {http://www.astron.nl/SIP-Lofar}Length with content type SIMPLE
class Length (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Length with content type SIMPLE"""
    _TypeDefinition = pyxb.binding.datatypes.double
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Length')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 45, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.double
    
    # Attribute units uses Python identifier units
    __units = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'units'), 'units', '__httpwww_astron_nlSIP_Lofar_Length_units', _module_typeBindings.LengthUnit, required=True)
    __units._DeclarationLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 48, 4)
    __units._UseLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 48, 4)
    
    units = property(__units.value, __units.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __units.name() : __units
    })
_module_typeBindings.Length = Length
Namespace.addCategoryObject('typeBinding', 'Length', Length)


# Complex type {http://www.astron.nl/SIP-Lofar}Time with content type SIMPLE
class Time (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Time with content type SIMPLE"""
    _TypeDefinition = pyxb.binding.datatypes.double
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Time')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 60, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.double
    
    # Attribute units uses Python identifier units
    __units = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'units'), 'units', '__httpwww_astron_nlSIP_Lofar_Time_units', _module_typeBindings.TimeUnit, required=True)
    __units._DeclarationLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 63, 4)
    __units._UseLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 63, 4)
    
    units = property(__units.value, __units.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __units.name() : __units
    })
_module_typeBindings.Time = Time
Namespace.addCategoryObject('typeBinding', 'Time', Time)


# Complex type {http://www.astron.nl/SIP-Lofar}Angle with content type SIMPLE
class Angle (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Angle with content type SIMPLE"""
    _TypeDefinition = pyxb.binding.datatypes.double
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Angle')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 74, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.double
    
    # Attribute units uses Python identifier units
    __units = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'units'), 'units', '__httpwww_astron_nlSIP_Lofar_Angle_units', _module_typeBindings.AngleUnit, required=True)
    __units._DeclarationLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 77, 4)
    __units._UseLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 77, 4)
    
    units = property(__units.value, __units.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __units.name() : __units
    })
_module_typeBindings.Angle = Angle
Namespace.addCategoryObject('typeBinding', 'Angle', Angle)


# Complex type {http://www.astron.nl/SIP-Lofar}Pixel with content type SIMPLE
class Pixel (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://www.astron.nl/SIP-Lofar}Pixel with content type SIMPLE"""
    _TypeDefinition = pyxb.binding.datatypes.double
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Pixel')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 86, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.double
    
    # Attribute units uses Python identifier units
    __units = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'units'), 'units', '__httpwww_astron_nlSIP_Lofar_Pixel_units', _module_typeBindings.PixelUnit, required=True)
    __units._DeclarationLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 89, 4)
    __units._UseLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 89, 4)
    
    units = property(__units.value, __units.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __units.name() : __units
    })
_module_typeBindings.Pixel = Pixel
Namespace.addCategoryObject('typeBinding', 'Pixel', Pixel)


# Complex type {http://www.astron.nl/SIP-Lofar}Observation with content type ELEMENT_ONLY
class Observation (Process):
    """Complex type {http://www.astron.nl/SIP-Lofar}Observation with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Observation')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 350, 1)
    _ElementMap = Process._ElementMap.copy()
    _AttributeMap = Process._AttributeMap.copy()
    # Base type is Process
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observingMode uses Python identifier observingMode
    __observingMode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observingMode'), 'observingMode', '__httpwww_astron_nlSIP_Lofar_Observation_observingMode', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 354, 5), )

    
    observingMode = property(__observingMode.value, __observingMode.set, None, None)

    
    # Element observationDescription uses Python identifier observationDescription
    __observationDescription = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observationDescription'), 'observationDescription', '__httpwww_astron_nlSIP_Lofar_Observation_observationDescription', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 355, 5), )

    
    observationDescription = property(__observationDescription.value, __observationDescription.set, None, None)

    
    # Element instrumentFilter uses Python identifier instrumentFilter
    __instrumentFilter = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'instrumentFilter'), 'instrumentFilter', '__httpwww_astron_nlSIP_Lofar_Observation_instrumentFilter', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 356, 5), )

    
    instrumentFilter = property(__instrumentFilter.value, __instrumentFilter.set, None, None)

    
    # Element clock uses Python identifier clock
    __clock = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'clock'), 'clock', '__httpwww_astron_nlSIP_Lofar_Observation_clock', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 357, 5), )

    
    clock = property(__clock.value, __clock.set, None, None)

    
    # Element stationSelection uses Python identifier stationSelection
    __stationSelection = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stationSelection'), 'stationSelection', '__httpwww_astron_nlSIP_Lofar_Observation_stationSelection', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 358, 5), )

    
    stationSelection = property(__stationSelection.value, __stationSelection.set, None, None)

    
    # Element antennaSet uses Python identifier antennaSet
    __antennaSet = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'antennaSet'), 'antennaSet', '__httpwww_astron_nlSIP_Lofar_Observation_antennaSet', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 359, 5), )

    
    antennaSet = property(__antennaSet.value, __antennaSet.set, None, None)

    
    # Element timeSystem uses Python identifier timeSystem
    __timeSystem = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeSystem'), 'timeSystem', '__httpwww_astron_nlSIP_Lofar_Observation_timeSystem', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 360, 5), )

    
    timeSystem = property(__timeSystem.value, __timeSystem.set, None, None)

    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_Observation_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 361, 5), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_Observation_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 362, 5), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    
    # Element numberOfStations uses Python identifier numberOfStations
    __numberOfStations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfStations'), 'numberOfStations', '__httpwww_astron_nlSIP_Lofar_Observation_numberOfStations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 363, 5), )

    
    numberOfStations = property(__numberOfStations.value, __numberOfStations.set, None, None)

    
    # Element stations uses Python identifier stations
    __stations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stations'), 'stations', '__httpwww_astron_nlSIP_Lofar_Observation_stations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 364, 5), )

    
    stations = property(__stations.value, __stations.set, None, None)

    
    # Element numberOfSubArrayPointings uses Python identifier numberOfSubArrayPointings
    __numberOfSubArrayPointings = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfSubArrayPointings'), 'numberOfSubArrayPointings', '__httpwww_astron_nlSIP_Lofar_Observation_numberOfSubArrayPointings', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 365, 5), )

    
    numberOfSubArrayPointings = property(__numberOfSubArrayPointings.value, __numberOfSubArrayPointings.set, None, None)

    
    # Element subArrayPointings uses Python identifier subArrayPointings
    __subArrayPointings = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subArrayPointings'), 'subArrayPointings', '__httpwww_astron_nlSIP_Lofar_Observation_subArrayPointings', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 366, 5), )

    
    subArrayPointings = property(__subArrayPointings.value, __subArrayPointings.set, None, None)

    
    # Element numberOftransientBufferBoardEvents uses Python identifier numberOftransientBufferBoardEvents
    __numberOftransientBufferBoardEvents = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOftransientBufferBoardEvents'), 'numberOftransientBufferBoardEvents', '__httpwww_astron_nlSIP_Lofar_Observation_numberOftransientBufferBoardEvents', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 367, 5), )

    
    numberOftransientBufferBoardEvents = property(__numberOftransientBufferBoardEvents.value, __numberOftransientBufferBoardEvents.set, None, None)

    
    # Element transientBufferBoardEvents uses Python identifier transientBufferBoardEvents
    __transientBufferBoardEvents = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'transientBufferBoardEvents'), 'transientBufferBoardEvents', '__httpwww_astron_nlSIP_Lofar_Observation_transientBufferBoardEvents', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 368, 5), )

    
    transientBufferBoardEvents = property(__transientBufferBoardEvents.value, __transientBufferBoardEvents.set, None, None)

    
    # Element numberOfCorrelatedDataProducts uses Python identifier numberOfCorrelatedDataProducts
    __numberOfCorrelatedDataProducts = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), 'numberOfCorrelatedDataProducts', '__httpwww_astron_nlSIP_Lofar_Observation_numberOfCorrelatedDataProducts', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 369, 5), )

    
    numberOfCorrelatedDataProducts = property(__numberOfCorrelatedDataProducts.value, __numberOfCorrelatedDataProducts.set, None, None)

    
    # Element numberOfBeamFormedDataProducts uses Python identifier numberOfBeamFormedDataProducts
    __numberOfBeamFormedDataProducts = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfBeamFormedDataProducts'), 'numberOfBeamFormedDataProducts', '__httpwww_astron_nlSIP_Lofar_Observation_numberOfBeamFormedDataProducts', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 370, 5), )

    
    numberOfBeamFormedDataProducts = property(__numberOfBeamFormedDataProducts.value, __numberOfBeamFormedDataProducts.set, None, None)

    
    # Element numberOfBitsPerSample uses Python identifier numberOfBitsPerSample
    __numberOfBitsPerSample = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfBitsPerSample'), 'numberOfBitsPerSample', '__httpwww_astron_nlSIP_Lofar_Observation_numberOfBitsPerSample', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 371, 5), )

    
    numberOfBitsPerSample = property(__numberOfBitsPerSample.value, __numberOfBitsPerSample.set, None, None)

    _ElementMap.update({
        __observingMode.name() : __observingMode,
        __observationDescription.name() : __observationDescription,
        __instrumentFilter.name() : __instrumentFilter,
        __clock.name() : __clock,
        __stationSelection.name() : __stationSelection,
        __antennaSet.name() : __antennaSet,
        __timeSystem.name() : __timeSystem,
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband,
        __numberOfStations.name() : __numberOfStations,
        __stations.name() : __stations,
        __numberOfSubArrayPointings.name() : __numberOfSubArrayPointings,
        __subArrayPointings.name() : __subArrayPointings,
        __numberOftransientBufferBoardEvents.name() : __numberOftransientBufferBoardEvents,
        __transientBufferBoardEvents.name() : __transientBufferBoardEvents,
        __numberOfCorrelatedDataProducts.name() : __numberOfCorrelatedDataProducts,
        __numberOfBeamFormedDataProducts.name() : __numberOfBeamFormedDataProducts,
        __numberOfBitsPerSample.name() : __numberOfBitsPerSample
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Observation = Observation
Namespace.addCategoryObject('typeBinding', 'Observation', Observation)


# Complex type {http://www.astron.nl/SIP-Lofar}DirectDataMeasurement with content type ELEMENT_ONLY
class DirectDataMeasurement (Process):
    """Complex type {http://www.astron.nl/SIP-Lofar}DirectDataMeasurement with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DirectDataMeasurement')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 376, 1)
    _ElementMap = Process._ElementMap.copy()
    _AttributeMap = Process._AttributeMap.copy()
    # Base type is Process
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observingMode uses Python identifier observingMode
    __observingMode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observingMode'), 'observingMode', '__httpwww_astron_nlSIP_Lofar_DirectDataMeasurement_observingMode', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 380, 5), )

    
    observingMode = property(__observingMode.value, __observingMode.set, None, None)

    
    # Element station uses Python identifier station
    __station = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'station'), 'station', '__httpwww_astron_nlSIP_Lofar_DirectDataMeasurement_station', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 381, 5), )

    
    station = property(__station.value, __station.set, None, None)

    _ElementMap.update({
        __observingMode.name() : __observingMode,
        __station.name() : __station
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.DirectDataMeasurement = DirectDataMeasurement
Namespace.addCategoryObject('typeBinding', 'DirectDataMeasurement', DirectDataMeasurement)


# Complex type {http://www.astron.nl/SIP-Lofar}GenericMeasurement with content type ELEMENT_ONLY
class GenericMeasurement (Process):
    """Complex type {http://www.astron.nl/SIP-Lofar}GenericMeasurement with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GenericMeasurement')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 393, 1)
    _ElementMap = Process._ElementMap.copy()
    _AttributeMap = Process._AttributeMap.copy()
    # Base type is Process
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observingMode uses Python identifier observingMode
    __observingMode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observingMode'), 'observingMode', '__httpwww_astron_nlSIP_Lofar_GenericMeasurement_observingMode', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 397, 5), )

    
    observingMode = property(__observingMode.value, __observingMode.set, None, None)

    
    # Element description uses Python identifier description
    __description = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'description'), 'description', '__httpwww_astron_nlSIP_Lofar_GenericMeasurement_description', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 398, 5), )

    
    description = property(__description.value, __description.set, None, None)

    _ElementMap.update({
        __observingMode.name() : __observingMode,
        __description.name() : __description
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.GenericMeasurement = GenericMeasurement
Namespace.addCategoryObject('typeBinding', 'GenericMeasurement', GenericMeasurement)


# Complex type {http://www.astron.nl/SIP-Lofar}UnspecifiedProcess with content type ELEMENT_ONLY
class UnspecifiedProcess (Process):
    """Complex type {http://www.astron.nl/SIP-Lofar}UnspecifiedProcess with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'UnspecifiedProcess')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 403, 1)
    _ElementMap = Process._ElementMap.copy()
    _AttributeMap = Process._AttributeMap.copy()
    # Base type is Process
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observingMode uses Python identifier observingMode
    __observingMode = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observingMode'), 'observingMode', '__httpwww_astron_nlSIP_Lofar_UnspecifiedProcess_observingMode', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 407, 5), )

    
    observingMode = property(__observingMode.value, __observingMode.set, None, None)

    
    # Element description uses Python identifier description
    __description = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'description'), 'description', '__httpwww_astron_nlSIP_Lofar_UnspecifiedProcess_description', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 408, 5), )

    
    description = property(__description.value, __description.set, None, None)

    _ElementMap.update({
        __observingMode.name() : __observingMode,
        __description.name() : __description
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.UnspecifiedProcess = UnspecifiedProcess
Namespace.addCategoryObject('typeBinding', 'UnspecifiedProcess', UnspecifiedProcess)


# Complex type {http://www.astron.nl/SIP-Lofar}Correlator with content type ELEMENT_ONLY
class Correlator (RealTimeProcess):
    """Complex type {http://www.astron.nl/SIP-Lofar}Correlator with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Correlator')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 453, 1)
    _ElementMap = RealTimeProcess._ElementMap.copy()
    _AttributeMap = RealTimeProcess._AttributeMap.copy()
    # Base type is RealTimeProcess
    
    # Element processingType (processingType) inherited from {http://www.astron.nl/SIP-Lofar}RealTimeProcess
    
    # Element integrationInterval uses Python identifier integrationInterval
    __integrationInterval = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'integrationInterval'), 'integrationInterval', '__httpwww_astron_nlSIP_Lofar_Correlator_integrationInterval', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 457, 5), )

    
    integrationInterval = property(__integrationInterval.value, __integrationInterval.set, None, None)

    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_Correlator_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 458, 5), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_Correlator_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 459, 5), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    _ElementMap.update({
        __integrationInterval.name() : __integrationInterval,
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.Correlator = Correlator
Namespace.addCategoryObject('typeBinding', 'Correlator', Correlator)


# Complex type {http://www.astron.nl/SIP-Lofar}CoherentStokes with content type ELEMENT_ONLY
class CoherentStokes (RealTimeProcess):
    """Complex type {http://www.astron.nl/SIP-Lofar}CoherentStokes with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CoherentStokes')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 474, 1)
    _ElementMap = RealTimeProcess._ElementMap.copy()
    _AttributeMap = RealTimeProcess._AttributeMap.copy()
    # Base type is RealTimeProcess
    
    # Element processingType (processingType) inherited from {http://www.astron.nl/SIP-Lofar}RealTimeProcess
    
    # Element rawSamplingTime uses Python identifier rawSamplingTime
    __rawSamplingTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'rawSamplingTime'), 'rawSamplingTime', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_rawSamplingTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 478, 5), )

    
    rawSamplingTime = property(__rawSamplingTime.value, __rawSamplingTime.set, None, None)

    
    # Element timeDownsamplingFactor uses Python identifier timeDownsamplingFactor
    __timeDownsamplingFactor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor'), 'timeDownsamplingFactor', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_timeDownsamplingFactor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 479, 5), )

    
    timeDownsamplingFactor = property(__timeDownsamplingFactor.value, __timeDownsamplingFactor.set, None, None)

    
    # Element samplingTime uses Python identifier samplingTime
    __samplingTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'samplingTime'), 'samplingTime', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_samplingTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 480, 5), )

    
    samplingTime = property(__samplingTime.value, __samplingTime.set, None, None)

    
    # Element frequencyDownsamplingFactor uses Python identifier frequencyDownsamplingFactor
    __frequencyDownsamplingFactor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'frequencyDownsamplingFactor'), 'frequencyDownsamplingFactor', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_frequencyDownsamplingFactor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 481, 5), )

    
    frequencyDownsamplingFactor = property(__frequencyDownsamplingFactor.value, __frequencyDownsamplingFactor.set, None, None)

    
    # Element numberOfCollapsedChannels uses Python identifier numberOfCollapsedChannels
    __numberOfCollapsedChannels = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCollapsedChannels'), 'numberOfCollapsedChannels', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_numberOfCollapsedChannels', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 482, 5), )

    
    numberOfCollapsedChannels = property(__numberOfCollapsedChannels.value, __numberOfCollapsedChannels.set, None, None)

    
    # Element stokes uses Python identifier stokes
    __stokes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stokes'), 'stokes', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_stokes', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 483, 5), )

    
    stokes = property(__stokes.value, __stokes.set, None, None)

    
    # Element numberOfStations uses Python identifier numberOfStations
    __numberOfStations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfStations'), 'numberOfStations', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_numberOfStations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 484, 5), )

    
    numberOfStations = property(__numberOfStations.value, __numberOfStations.set, None, None)

    
    # Element stations uses Python identifier stations
    __stations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stations'), 'stations', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_stations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 485, 5), )

    
    stations = property(__stations.value, __stations.set, None, None)

    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 486, 5), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_CoherentStokes_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 487, 5), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    _ElementMap.update({
        __rawSamplingTime.name() : __rawSamplingTime,
        __timeDownsamplingFactor.name() : __timeDownsamplingFactor,
        __samplingTime.name() : __samplingTime,
        __frequencyDownsamplingFactor.name() : __frequencyDownsamplingFactor,
        __numberOfCollapsedChannels.name() : __numberOfCollapsedChannels,
        __stokes.name() : __stokes,
        __numberOfStations.name() : __numberOfStations,
        __stations.name() : __stations,
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CoherentStokes = CoherentStokes
Namespace.addCategoryObject('typeBinding', 'CoherentStokes', CoherentStokes)


# Complex type {http://www.astron.nl/SIP-Lofar}IncoherentStokes with content type ELEMENT_ONLY
class IncoherentStokes (RealTimeProcess):
    """Complex type {http://www.astron.nl/SIP-Lofar}IncoherentStokes with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'IncoherentStokes')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 492, 1)
    _ElementMap = RealTimeProcess._ElementMap.copy()
    _AttributeMap = RealTimeProcess._AttributeMap.copy()
    # Base type is RealTimeProcess
    
    # Element processingType (processingType) inherited from {http://www.astron.nl/SIP-Lofar}RealTimeProcess
    
    # Element rawSamplingTime uses Python identifier rawSamplingTime
    __rawSamplingTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'rawSamplingTime'), 'rawSamplingTime', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_rawSamplingTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 496, 5), )

    
    rawSamplingTime = property(__rawSamplingTime.value, __rawSamplingTime.set, None, None)

    
    # Element timeDownsamplingFactor uses Python identifier timeDownsamplingFactor
    __timeDownsamplingFactor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor'), 'timeDownsamplingFactor', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_timeDownsamplingFactor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 497, 5), )

    
    timeDownsamplingFactor = property(__timeDownsamplingFactor.value, __timeDownsamplingFactor.set, None, None)

    
    # Element samplingTime uses Python identifier samplingTime
    __samplingTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'samplingTime'), 'samplingTime', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_samplingTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 498, 5), )

    
    samplingTime = property(__samplingTime.value, __samplingTime.set, None, None)

    
    # Element frequencyDownsamplingFactor uses Python identifier frequencyDownsamplingFactor
    __frequencyDownsamplingFactor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'frequencyDownsamplingFactor'), 'frequencyDownsamplingFactor', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_frequencyDownsamplingFactor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 499, 5), )

    
    frequencyDownsamplingFactor = property(__frequencyDownsamplingFactor.value, __frequencyDownsamplingFactor.set, None, None)

    
    # Element numberOfCollapsedChannels uses Python identifier numberOfCollapsedChannels
    __numberOfCollapsedChannels = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCollapsedChannels'), 'numberOfCollapsedChannels', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_numberOfCollapsedChannels', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 500, 5), )

    
    numberOfCollapsedChannels = property(__numberOfCollapsedChannels.value, __numberOfCollapsedChannels.set, None, None)

    
    # Element stokes uses Python identifier stokes
    __stokes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stokes'), 'stokes', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_stokes', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 501, 5), )

    
    stokes = property(__stokes.value, __stokes.set, None, None)

    
    # Element numberOfStations uses Python identifier numberOfStations
    __numberOfStations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfStations'), 'numberOfStations', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_numberOfStations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 502, 5), )

    
    numberOfStations = property(__numberOfStations.value, __numberOfStations.set, None, None)

    
    # Element stations uses Python identifier stations
    __stations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stations'), 'stations', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_stations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 503, 5), )

    
    stations = property(__stations.value, __stations.set, None, None)

    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 504, 5), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_IncoherentStokes_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 505, 5), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    _ElementMap.update({
        __rawSamplingTime.name() : __rawSamplingTime,
        __timeDownsamplingFactor.name() : __timeDownsamplingFactor,
        __samplingTime.name() : __samplingTime,
        __frequencyDownsamplingFactor.name() : __frequencyDownsamplingFactor,
        __numberOfCollapsedChannels.name() : __numberOfCollapsedChannels,
        __stokes.name() : __stokes,
        __numberOfStations.name() : __numberOfStations,
        __stations.name() : __stations,
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.IncoherentStokes = IncoherentStokes
Namespace.addCategoryObject('typeBinding', 'IncoherentStokes', IncoherentStokes)


# Complex type {http://www.astron.nl/SIP-Lofar}FlysEye with content type ELEMENT_ONLY
class FlysEye (RealTimeProcess):
    """Complex type {http://www.astron.nl/SIP-Lofar}FlysEye with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FlysEye')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 510, 1)
    _ElementMap = RealTimeProcess._ElementMap.copy()
    _AttributeMap = RealTimeProcess._AttributeMap.copy()
    # Base type is RealTimeProcess
    
    # Element processingType (processingType) inherited from {http://www.astron.nl/SIP-Lofar}RealTimeProcess
    
    # Element rawSamplingTime uses Python identifier rawSamplingTime
    __rawSamplingTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'rawSamplingTime'), 'rawSamplingTime', '__httpwww_astron_nlSIP_Lofar_FlysEye_rawSamplingTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 514, 5), )

    
    rawSamplingTime = property(__rawSamplingTime.value, __rawSamplingTime.set, None, None)

    
    # Element timeDownsamplingFactor uses Python identifier timeDownsamplingFactor
    __timeDownsamplingFactor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor'), 'timeDownsamplingFactor', '__httpwww_astron_nlSIP_Lofar_FlysEye_timeDownsamplingFactor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 515, 5), )

    
    timeDownsamplingFactor = property(__timeDownsamplingFactor.value, __timeDownsamplingFactor.set, None, None)

    
    # Element samplingTime uses Python identifier samplingTime
    __samplingTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'samplingTime'), 'samplingTime', '__httpwww_astron_nlSIP_Lofar_FlysEye_samplingTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 516, 5), )

    
    samplingTime = property(__samplingTime.value, __samplingTime.set, None, None)

    
    # Element stokes uses Python identifier stokes
    __stokes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stokes'), 'stokes', '__httpwww_astron_nlSIP_Lofar_FlysEye_stokes', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 517, 5), )

    
    stokes = property(__stokes.value, __stokes.set, None, None)

    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_FlysEye_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 518, 5), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_FlysEye_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 519, 5), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    _ElementMap.update({
        __rawSamplingTime.name() : __rawSamplingTime,
        __timeDownsamplingFactor.name() : __timeDownsamplingFactor,
        __samplingTime.name() : __samplingTime,
        __stokes.name() : __stokes,
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.FlysEye = FlysEye
Namespace.addCategoryObject('typeBinding', 'FlysEye', FlysEye)


# Complex type {http://www.astron.nl/SIP-Lofar}NonStandard with content type ELEMENT_ONLY
class NonStandard (RealTimeProcess):
    """Complex type {http://www.astron.nl/SIP-Lofar}NonStandard with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NonStandard')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 524, 1)
    _ElementMap = RealTimeProcess._ElementMap.copy()
    _AttributeMap = RealTimeProcess._AttributeMap.copy()
    # Base type is RealTimeProcess
    
    # Element processingType (processingType) inherited from {http://www.astron.nl/SIP-Lofar}RealTimeProcess
    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_NonStandard_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 528, 5), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_NonStandard_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 529, 5), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    _ElementMap.update({
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.NonStandard = NonStandard
Namespace.addCategoryObject('typeBinding', 'NonStandard', NonStandard)


# Complex type {http://www.astron.nl/SIP-Lofar}PipelineRun with content type ELEMENT_ONLY
class PipelineRun (Process):
    """Complex type {http://www.astron.nl/SIP-Lofar}PipelineRun with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PipelineRun')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 585, 1)
    _ElementMap = Process._ElementMap.copy()
    _AttributeMap = Process._AttributeMap.copy()
    # Base type is Process
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName uses Python identifier pipelineName
    __pipelineName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'pipelineName'), 'pipelineName', '__httpwww_astron_nlSIP_Lofar_PipelineRun_pipelineName', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5), )

    
    pipelineName = property(__pipelineName.value, __pipelineName.set, None, None)

    
    # Element pipelineVersion uses Python identifier pipelineVersion
    __pipelineVersion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'pipelineVersion'), 'pipelineVersion', '__httpwww_astron_nlSIP_Lofar_PipelineRun_pipelineVersion', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5), )

    
    pipelineVersion = property(__pipelineVersion.value, __pipelineVersion.set, None, None)

    
    # Element sourceData uses Python identifier sourceData
    __sourceData = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'sourceData'), 'sourceData', '__httpwww_astron_nlSIP_Lofar_PipelineRun_sourceData', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5), )

    
    sourceData = property(__sourceData.value, __sourceData.set, None, None)

    _ElementMap.update({
        __pipelineName.name() : __pipelineName,
        __pipelineVersion.name() : __pipelineVersion,
        __sourceData.name() : __sourceData
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.PipelineRun = PipelineRun
Namespace.addCategoryObject('typeBinding', 'PipelineRun', PipelineRun)


# Complex type {http://www.astron.nl/SIP-Lofar}CorrelatedDataProduct with content type ELEMENT_ONLY
class CorrelatedDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}CorrelatedDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CorrelatedDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 808, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element subArrayPointingIdentifier uses Python identifier subArrayPointingIdentifier
    __subArrayPointingIdentifier = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier'), 'subArrayPointingIdentifier', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_subArrayPointingIdentifier', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 812, 5), )

    
    subArrayPointingIdentifier = property(__subArrayPointingIdentifier.value, __subArrayPointingIdentifier.set, None, None)

    
    # Element subband uses Python identifier subband
    __subband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subband'), 'subband', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_subband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 813, 5), )

    
    subband = property(__subband.value, __subband.set, None, None)

    
    # Element stationSubband uses Python identifier stationSubband
    __stationSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'stationSubband'), 'stationSubband', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_stationSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 814, 5), )

    
    stationSubband = property(__stationSubband.value, __stationSubband.set, None, None)

    
    # Element startTime uses Python identifier startTime
    __startTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'startTime'), 'startTime', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_startTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 815, 5), )

    
    startTime = property(__startTime.value, __startTime.set, None, None)

    
    # Element duration uses Python identifier duration
    __duration = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'duration'), 'duration', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_duration', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 816, 5), )

    
    duration = property(__duration.value, __duration.set, None, None)

    
    # Element integrationInterval uses Python identifier integrationInterval
    __integrationInterval = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'integrationInterval'), 'integrationInterval', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_integrationInterval', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 817, 5), )

    
    integrationInterval = property(__integrationInterval.value, __integrationInterval.set, None, None)

    
    # Element centralFrequency uses Python identifier centralFrequency
    __centralFrequency = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'centralFrequency'), 'centralFrequency', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_centralFrequency', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 818, 5), )

    
    centralFrequency = property(__centralFrequency.value, __centralFrequency.set, None, None)

    
    # Element channelWidth uses Python identifier channelWidth
    __channelWidth = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelWidth'), 'channelWidth', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_channelWidth', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 819, 5), )

    
    channelWidth = property(__channelWidth.value, __channelWidth.set, None, None)

    
    # Element channelsPerSubband uses Python identifier channelsPerSubband
    __channelsPerSubband = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), 'channelsPerSubband', '__httpwww_astron_nlSIP_Lofar_CorrelatedDataProduct_channelsPerSubband', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 820, 5), )

    
    channelsPerSubband = property(__channelsPerSubband.value, __channelsPerSubband.set, None, None)

    _ElementMap.update({
        __subArrayPointingIdentifier.name() : __subArrayPointingIdentifier,
        __subband.name() : __subband,
        __stationSubband.name() : __stationSubband,
        __startTime.name() : __startTime,
        __duration.name() : __duration,
        __integrationInterval.name() : __integrationInterval,
        __centralFrequency.name() : __centralFrequency,
        __channelWidth.name() : __channelWidth,
        __channelsPerSubband.name() : __channelsPerSubband
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CorrelatedDataProduct = CorrelatedDataProduct
Namespace.addCategoryObject('typeBinding', 'CorrelatedDataProduct', CorrelatedDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}InstrumentModelDataProduct with content type ELEMENT_ONLY
class InstrumentModelDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}InstrumentModelDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'InstrumentModelDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 830, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.InstrumentModelDataProduct = InstrumentModelDataProduct
Namespace.addCategoryObject('typeBinding', 'InstrumentModelDataProduct', InstrumentModelDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}SkyModelDataProduct with content type ELEMENT_ONLY
class SkyModelDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}SkyModelDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SkyModelDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 840, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.SkyModelDataProduct = SkyModelDataProduct
Namespace.addCategoryObject('typeBinding', 'SkyModelDataProduct', SkyModelDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}TransientBufferBoardDataProduct with content type ELEMENT_ONLY
class TransientBufferBoardDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}TransientBufferBoardDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TransientBufferBoardDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 851, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element numberOfSamples uses Python identifier numberOfSamples
    __numberOfSamples = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfSamples'), 'numberOfSamples', '__httpwww_astron_nlSIP_Lofar_TransientBufferBoardDataProduct_numberOfSamples', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 855, 5), )

    
    numberOfSamples = property(__numberOfSamples.value, __numberOfSamples.set, None, None)

    
    # Element timeStamp uses Python identifier timeStamp
    __timeStamp = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeStamp'), 'timeStamp', '__httpwww_astron_nlSIP_Lofar_TransientBufferBoardDataProduct_timeStamp', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 856, 5), )

    
    timeStamp = property(__timeStamp.value, __timeStamp.set, None, None)

    
    # Element triggerParameters uses Python identifier triggerParameters
    __triggerParameters = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'triggerParameters'), 'triggerParameters', '__httpwww_astron_nlSIP_Lofar_TransientBufferBoardDataProduct_triggerParameters', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 857, 5), )

    
    triggerParameters = property(__triggerParameters.value, __triggerParameters.set, None, None)

    _ElementMap.update({
        __numberOfSamples.name() : __numberOfSamples,
        __timeStamp.name() : __timeStamp,
        __triggerParameters.name() : __triggerParameters
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.TransientBufferBoardDataProduct = TransientBufferBoardDataProduct
Namespace.addCategoryObject('typeBinding', 'TransientBufferBoardDataProduct', TransientBufferBoardDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}CoherentStokesBeam with content type ELEMENT_ONLY
class CoherentStokesBeam (ArrayBeam):
    """Complex type {http://www.astron.nl/SIP-Lofar}CoherentStokesBeam with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CoherentStokesBeam')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 896, 1)
    _ElementMap = ArrayBeam._ElementMap.copy()
    _AttributeMap = ArrayBeam._AttributeMap.copy()
    # Base type is ArrayBeam
    
    # Element subArrayPointingIdentifier (subArrayPointingIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element beamNumber (beamNumber) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element dispersionMeasure (dispersionMeasure) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element numberOfSubbands (numberOfSubbands) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element stationSubbands (stationSubbands) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element samplingTime (samplingTime) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element centralFrequencies (centralFrequencies) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element channelWidth (channelWidth) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element channelsPerSubband (channelsPerSubband) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element stokes (stokes) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element pointing uses Python identifier pointing
    __pointing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'pointing'), 'pointing', '__httpwww_astron_nlSIP_Lofar_CoherentStokesBeam_pointing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 900, 5), )

    
    pointing = property(__pointing.value, __pointing.set, None, None)

    
    # Element offset uses Python identifier offset
    __offset = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'offset'), 'offset', '__httpwww_astron_nlSIP_Lofar_CoherentStokesBeam_offset', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 901, 5), )

    
    offset = property(__offset.value, __offset.set, None, None)

    _ElementMap.update({
        __pointing.name() : __pointing,
        __offset.name() : __offset
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CoherentStokesBeam = CoherentStokesBeam
Namespace.addCategoryObject('typeBinding', 'CoherentStokesBeam', CoherentStokesBeam)


# Complex type {http://www.astron.nl/SIP-Lofar}IncoherentStokesBeam with content type ELEMENT_ONLY
class IncoherentStokesBeam (ArrayBeam):
    """Complex type {http://www.astron.nl/SIP-Lofar}IncoherentStokesBeam with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'IncoherentStokesBeam')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 906, 1)
    _ElementMap = ArrayBeam._ElementMap.copy()
    _AttributeMap = ArrayBeam._AttributeMap.copy()
    # Base type is ArrayBeam
    
    # Element subArrayPointingIdentifier (subArrayPointingIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element beamNumber (beamNumber) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element dispersionMeasure (dispersionMeasure) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element numberOfSubbands (numberOfSubbands) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element stationSubbands (stationSubbands) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element samplingTime (samplingTime) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element centralFrequencies (centralFrequencies) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element channelWidth (channelWidth) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element channelsPerSubband (channelsPerSubband) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element stokes (stokes) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.IncoherentStokesBeam = IncoherentStokesBeam
Namespace.addCategoryObject('typeBinding', 'IncoherentStokesBeam', IncoherentStokesBeam)


# Complex type {http://www.astron.nl/SIP-Lofar}FlysEyeBeam with content type ELEMENT_ONLY
class FlysEyeBeam (ArrayBeam):
    """Complex type {http://www.astron.nl/SIP-Lofar}FlysEyeBeam with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'FlysEyeBeam')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 913, 1)
    _ElementMap = ArrayBeam._ElementMap.copy()
    _AttributeMap = ArrayBeam._AttributeMap.copy()
    # Base type is ArrayBeam
    
    # Element subArrayPointingIdentifier (subArrayPointingIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element beamNumber (beamNumber) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element dispersionMeasure (dispersionMeasure) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element numberOfSubbands (numberOfSubbands) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element stationSubbands (stationSubbands) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element samplingTime (samplingTime) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element centralFrequencies (centralFrequencies) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element channelWidth (channelWidth) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element channelsPerSubband (channelsPerSubband) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element stokes (stokes) inherited from {http://www.astron.nl/SIP-Lofar}ArrayBeam
    
    # Element station uses Python identifier station
    __station = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'station'), 'station', '__httpwww_astron_nlSIP_Lofar_FlysEyeBeam_station', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 917, 5), )

    
    station = property(__station.value, __station.set, None, None)

    _ElementMap.update({
        __station.name() : __station
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.FlysEyeBeam = FlysEyeBeam
Namespace.addCategoryObject('typeBinding', 'FlysEyeBeam', FlysEyeBeam)


# Complex type {http://www.astron.nl/SIP-Lofar}BeamFormedDataProduct with content type ELEMENT_ONLY
class BeamFormedDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}BeamFormedDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'BeamFormedDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 922, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element numberOfBeams uses Python identifier numberOfBeams
    __numberOfBeams = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfBeams'), 'numberOfBeams', '__httpwww_astron_nlSIP_Lofar_BeamFormedDataProduct_numberOfBeams', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 926, 5), )

    
    numberOfBeams = property(__numberOfBeams.value, __numberOfBeams.set, None, None)

    
    # Element beams uses Python identifier beams
    __beams = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'beams'), 'beams', '__httpwww_astron_nlSIP_Lofar_BeamFormedDataProduct_beams', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 927, 5), )

    
    beams = property(__beams.value, __beams.set, None, None)

    _ElementMap.update({
        __numberOfBeams.name() : __numberOfBeams,
        __beams.name() : __beams
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.BeamFormedDataProduct = BeamFormedDataProduct
Namespace.addCategoryObject('typeBinding', 'BeamFormedDataProduct', BeamFormedDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}PulpSummaryDataProduct with content type ELEMENT_ONLY
class PulpSummaryDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}PulpSummaryDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PulpSummaryDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 949, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileContent uses Python identifier fileContent
    __fileContent = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'fileContent'), 'fileContent', '__httpwww_astron_nlSIP_Lofar_PulpSummaryDataProduct_fileContent', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 953, 5), )

    
    fileContent = property(__fileContent.value, __fileContent.set, None, None)

    
    # Element dataType uses Python identifier dataType
    __dataType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'dataType'), 'dataType', '__httpwww_astron_nlSIP_Lofar_PulpSummaryDataProduct_dataType', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 954, 5), )

    
    dataType = property(__dataType.value, __dataType.set, None, None)

    _ElementMap.update({
        __fileContent.name() : __fileContent,
        __dataType.name() : __dataType
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.PulpSummaryDataProduct = PulpSummaryDataProduct
Namespace.addCategoryObject('typeBinding', 'PulpSummaryDataProduct', PulpSummaryDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}PulpDataProduct with content type ELEMENT_ONLY
class PulpDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}PulpDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PulpDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 959, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileContent uses Python identifier fileContent
    __fileContent = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'fileContent'), 'fileContent', '__httpwww_astron_nlSIP_Lofar_PulpDataProduct_fileContent', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 963, 5), )

    
    fileContent = property(__fileContent.value, __fileContent.set, None, None)

    
    # Element dataType uses Python identifier dataType
    __dataType = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'dataType'), 'dataType', '__httpwww_astron_nlSIP_Lofar_PulpDataProduct_dataType', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 964, 5), )

    
    dataType = property(__dataType.value, __dataType.set, None, None)

    
    # Element arrayBeam uses Python identifier arrayBeam
    __arrayBeam = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'arrayBeam'), 'arrayBeam', '__httpwww_astron_nlSIP_Lofar_PulpDataProduct_arrayBeam', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 965, 5), )

    
    arrayBeam = property(__arrayBeam.value, __arrayBeam.set, None, None)

    _ElementMap.update({
        __fileContent.name() : __fileContent,
        __dataType.name() : __dataType,
        __arrayBeam.name() : __arrayBeam
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.PulpDataProduct = PulpDataProduct
Namespace.addCategoryObject('typeBinding', 'PulpDataProduct', PulpDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}GenericDataProduct with content type ELEMENT_ONLY
class GenericDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}GenericDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GenericDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 977, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.GenericDataProduct = GenericDataProduct
Namespace.addCategoryObject('typeBinding', 'GenericDataProduct', GenericDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}UnspecifiedDataProduct with content type ELEMENT_ONLY
class UnspecifiedDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}UnspecifiedDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'UnspecifiedDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 982, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.UnspecifiedDataProduct = UnspecifiedDataProduct
Namespace.addCategoryObject('typeBinding', 'UnspecifiedDataProduct', UnspecifiedDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}LinearAxis with content type ELEMENT_ONLY
class LinearAxis (Axis):
    """Complex type {http://www.astron.nl/SIP-Lofar}LinearAxis with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LinearAxis')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1002, 1)
    _ElementMap = Axis._ElementMap.copy()
    _AttributeMap = Axis._AttributeMap.copy()
    # Base type is Axis
    
    # Element number (number) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    
    # Element name (name) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    
    # Element units (units) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    
    # Element length (length) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    
    # Element increment uses Python identifier increment
    __increment = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'increment'), 'increment', '__httpwww_astron_nlSIP_Lofar_LinearAxis_increment', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1006, 5), )

    
    increment = property(__increment.value, __increment.set, None, None)

    
    # Element referencePixel uses Python identifier referencePixel
    __referencePixel = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'referencePixel'), 'referencePixel', '__httpwww_astron_nlSIP_Lofar_LinearAxis_referencePixel', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1007, 5), )

    
    referencePixel = property(__referencePixel.value, __referencePixel.set, None, None)

    
    # Element referenceValue uses Python identifier referenceValue
    __referenceValue = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'referenceValue'), 'referenceValue', '__httpwww_astron_nlSIP_Lofar_LinearAxis_referenceValue', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1008, 5), )

    
    referenceValue = property(__referenceValue.value, __referenceValue.set, None, None)

    _ElementMap.update({
        __increment.name() : __increment,
        __referencePixel.name() : __referencePixel,
        __referenceValue.name() : __referenceValue
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.LinearAxis = LinearAxis
Namespace.addCategoryObject('typeBinding', 'LinearAxis', LinearAxis)


# Complex type {http://www.astron.nl/SIP-Lofar}TabularAxis with content type ELEMENT_ONLY
class TabularAxis (Axis):
    """Complex type {http://www.astron.nl/SIP-Lofar}TabularAxis with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TabularAxis')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1013, 1)
    _ElementMap = Axis._ElementMap.copy()
    _AttributeMap = Axis._AttributeMap.copy()
    # Base type is Axis
    
    # Element number (number) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    
    # Element name (name) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    
    # Element units (units) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    
    # Element length (length) inherited from {http://www.astron.nl/SIP-Lofar}Axis
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.TabularAxis = TabularAxis
Namespace.addCategoryObject('typeBinding', 'TabularAxis', TabularAxis)


# Complex type {http://www.astron.nl/SIP-Lofar}DirectionCoordinate with content type ELEMENT_ONLY
class DirectionCoordinate (Coordinate):
    """Complex type {http://www.astron.nl/SIP-Lofar}DirectionCoordinate with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DirectionCoordinate')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1048, 1)
    _ElementMap = Coordinate._ElementMap.copy()
    _AttributeMap = Coordinate._AttributeMap.copy()
    # Base type is Coordinate
    
    # Element directionLinearAxis uses Python identifier directionLinearAxis
    __directionLinearAxis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'directionLinearAxis'), 'directionLinearAxis', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_directionLinearAxis', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1052, 5), )

    
    directionLinearAxis = property(__directionLinearAxis.value, __directionLinearAxis.set, None, None)

    
    # Element PC0_0 uses Python identifier PC0_0
    __PC0_0 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'PC0_0'), 'PC0_0', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_PC0_0', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1053, 5), )

    
    PC0_0 = property(__PC0_0.value, __PC0_0.set, None, None)

    
    # Element PC0_1 uses Python identifier PC0_1
    __PC0_1 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'PC0_1'), 'PC0_1', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_PC0_1', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1054, 5), )

    
    PC0_1 = property(__PC0_1.value, __PC0_1.set, None, None)

    
    # Element PC1_0 uses Python identifier PC1_0
    __PC1_0 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'PC1_0'), 'PC1_0', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_PC1_0', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1055, 5), )

    
    PC1_0 = property(__PC1_0.value, __PC1_0.set, None, None)

    
    # Element PC1_1 uses Python identifier PC1_1
    __PC1_1 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'PC1_1'), 'PC1_1', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_PC1_1', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1056, 5), )

    
    PC1_1 = property(__PC1_1.value, __PC1_1.set, None, None)

    
    # Element equinox uses Python identifier equinox
    __equinox = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'equinox'), 'equinox', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_equinox', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1057, 5), )

    
    equinox = property(__equinox.value, __equinox.set, None, None)

    
    # Element raDecSystem uses Python identifier raDecSystem
    __raDecSystem = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'raDecSystem'), 'raDecSystem', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_raDecSystem', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1058, 5), )

    
    raDecSystem = property(__raDecSystem.value, __raDecSystem.set, None, None)

    
    # Element projection uses Python identifier projection
    __projection = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'projection'), 'projection', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_projection', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1059, 5), )

    
    projection = property(__projection.value, __projection.set, None, None)

    
    # Element projectionParameters uses Python identifier projectionParameters
    __projectionParameters = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'projectionParameters'), 'projectionParameters', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_projectionParameters', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1060, 5), )

    
    projectionParameters = property(__projectionParameters.value, __projectionParameters.set, None, None)

    
    # Element longitudePole uses Python identifier longitudePole
    __longitudePole = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'longitudePole'), 'longitudePole', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_longitudePole', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1061, 5), )

    
    longitudePole = property(__longitudePole.value, __longitudePole.set, None, None)

    
    # Element latitudePole uses Python identifier latitudePole
    __latitudePole = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'latitudePole'), 'latitudePole', '__httpwww_astron_nlSIP_Lofar_DirectionCoordinate_latitudePole', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1062, 5), )

    
    latitudePole = property(__latitudePole.value, __latitudePole.set, None, None)

    _ElementMap.update({
        __directionLinearAxis.name() : __directionLinearAxis,
        __PC0_0.name() : __PC0_0,
        __PC0_1.name() : __PC0_1,
        __PC1_0.name() : __PC1_0,
        __PC1_1.name() : __PC1_1,
        __equinox.name() : __equinox,
        __raDecSystem.name() : __raDecSystem,
        __projection.name() : __projection,
        __projectionParameters.name() : __projectionParameters,
        __longitudePole.name() : __longitudePole,
        __latitudePole.name() : __latitudePole
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.DirectionCoordinate = DirectionCoordinate
Namespace.addCategoryObject('typeBinding', 'DirectionCoordinate', DirectionCoordinate)


# Complex type {http://www.astron.nl/SIP-Lofar}SpectralCoordinate with content type ELEMENT_ONLY
class SpectralCoordinate (Coordinate):
    """Complex type {http://www.astron.nl/SIP-Lofar}SpectralCoordinate with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SpectralCoordinate')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1087, 1)
    _ElementMap = Coordinate._ElementMap.copy()
    _AttributeMap = Coordinate._AttributeMap.copy()
    # Base type is Coordinate
    
    # Element spectralLinearAxis uses Python identifier spectralLinearAxis
    __spectralLinearAxis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'spectralLinearAxis'), 'spectralLinearAxis', '__httpwww_astron_nlSIP_Lofar_SpectralCoordinate_spectralLinearAxis', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1092, 6), )

    
    spectralLinearAxis = property(__spectralLinearAxis.value, __spectralLinearAxis.set, None, None)

    
    # Element spectralTabularAxis uses Python identifier spectralTabularAxis
    __spectralTabularAxis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'spectralTabularAxis'), 'spectralTabularAxis', '__httpwww_astron_nlSIP_Lofar_SpectralCoordinate_spectralTabularAxis', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1093, 6), )

    
    spectralTabularAxis = property(__spectralTabularAxis.value, __spectralTabularAxis.set, None, None)

    
    # Element spectralQuantity uses Python identifier spectralQuantity
    __spectralQuantity = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'spectralQuantity'), 'spectralQuantity', '__httpwww_astron_nlSIP_Lofar_SpectralCoordinate_spectralQuantity', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1095, 5), )

    
    spectralQuantity = property(__spectralQuantity.value, __spectralQuantity.set, None, None)

    _ElementMap.update({
        __spectralLinearAxis.name() : __spectralLinearAxis,
        __spectralTabularAxis.name() : __spectralTabularAxis,
        __spectralQuantity.name() : __spectralQuantity
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.SpectralCoordinate = SpectralCoordinate
Namespace.addCategoryObject('typeBinding', 'SpectralCoordinate', SpectralCoordinate)


# Complex type {http://www.astron.nl/SIP-Lofar}TimeCoordinate with content type ELEMENT_ONLY
class TimeCoordinate (Coordinate):
    """Complex type {http://www.astron.nl/SIP-Lofar}TimeCoordinate with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TimeCoordinate')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1100, 1)
    _ElementMap = Coordinate._ElementMap.copy()
    _AttributeMap = Coordinate._AttributeMap.copy()
    # Base type is Coordinate
    
    # Element timeLinearAxis uses Python identifier timeLinearAxis
    __timeLinearAxis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeLinearAxis'), 'timeLinearAxis', '__httpwww_astron_nlSIP_Lofar_TimeCoordinate_timeLinearAxis', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1105, 6), )

    
    timeLinearAxis = property(__timeLinearAxis.value, __timeLinearAxis.set, None, None)

    
    # Element timeTabularAxis uses Python identifier timeTabularAxis
    __timeTabularAxis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeTabularAxis'), 'timeTabularAxis', '__httpwww_astron_nlSIP_Lofar_TimeCoordinate_timeTabularAxis', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1106, 6), )

    
    timeTabularAxis = property(__timeTabularAxis.value, __timeTabularAxis.set, None, None)

    
    # Element equinox uses Python identifier equinox
    __equinox = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'equinox'), 'equinox', '__httpwww_astron_nlSIP_Lofar_TimeCoordinate_equinox', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1108, 5), )

    
    equinox = property(__equinox.value, __equinox.set, None, None)

    _ElementMap.update({
        __timeLinearAxis.name() : __timeLinearAxis,
        __timeTabularAxis.name() : __timeTabularAxis,
        __equinox.name() : __equinox
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.TimeCoordinate = TimeCoordinate
Namespace.addCategoryObject('typeBinding', 'TimeCoordinate', TimeCoordinate)


# Complex type {http://www.astron.nl/SIP-Lofar}PolarizationCoordinate with content type ELEMENT_ONLY
class PolarizationCoordinate (Coordinate):
    """Complex type {http://www.astron.nl/SIP-Lofar}PolarizationCoordinate with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PolarizationCoordinate')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1113, 1)
    _ElementMap = Coordinate._ElementMap.copy()
    _AttributeMap = Coordinate._AttributeMap.copy()
    # Base type is Coordinate
    
    # Element polarizationTabularAxis uses Python identifier polarizationTabularAxis
    __polarizationTabularAxis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'polarizationTabularAxis'), 'polarizationTabularAxis', '__httpwww_astron_nlSIP_Lofar_PolarizationCoordinate_polarizationTabularAxis', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1117, 5), )

    
    polarizationTabularAxis = property(__polarizationTabularAxis.value, __polarizationTabularAxis.set, None, None)

    
    # Element polarization uses Python identifier polarization
    __polarization = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'polarization'), 'polarization', '__httpwww_astron_nlSIP_Lofar_PolarizationCoordinate_polarization', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1118, 5), )

    
    polarization = property(__polarization.value, __polarization.set, None, None)

    _ElementMap.update({
        __polarizationTabularAxis.name() : __polarizationTabularAxis,
        __polarization.name() : __polarization
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.PolarizationCoordinate = PolarizationCoordinate
Namespace.addCategoryObject('typeBinding', 'PolarizationCoordinate', PolarizationCoordinate)


# Complex type {http://www.astron.nl/SIP-Lofar}PixelMapDataProduct with content type ELEMENT_ONLY
class PixelMapDataProduct (DataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}PixelMapDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PixelMapDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1128, 1)
    _ElementMap = DataProduct._ElementMap.copy()
    _AttributeMap = DataProduct._AttributeMap.copy()
    # Base type is DataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element numberOfAxes uses Python identifier numberOfAxes
    __numberOfAxes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfAxes'), 'numberOfAxes', '__httpwww_astron_nlSIP_Lofar_PixelMapDataProduct_numberOfAxes', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1132, 5), )

    
    numberOfAxes = property(__numberOfAxes.value, __numberOfAxes.set, None, None)

    
    # Element numberOfCoordinates uses Python identifier numberOfCoordinates
    __numberOfCoordinates = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCoordinates'), 'numberOfCoordinates', '__httpwww_astron_nlSIP_Lofar_PixelMapDataProduct_numberOfCoordinates', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1133, 5), )

    
    numberOfCoordinates = property(__numberOfCoordinates.value, __numberOfCoordinates.set, None, None)

    
    # Element coordinate uses Python identifier coordinate
    __coordinate = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'coordinate'), 'coordinate', '__httpwww_astron_nlSIP_Lofar_PixelMapDataProduct_coordinate', True, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1134, 5), )

    
    coordinate = property(__coordinate.value, __coordinate.set, None, None)

    _ElementMap.update({
        __numberOfAxes.name() : __numberOfAxes,
        __numberOfCoordinates.name() : __numberOfCoordinates,
        __coordinate.name() : __coordinate
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.PixelMapDataProduct = PixelMapDataProduct
Namespace.addCategoryObject('typeBinding', 'PixelMapDataProduct', PixelMapDataProduct)


# Complex type {http://www.astron.nl/SIP-Lofar}ClockType with content type SIMPLE
class ClockType (Frequency):
    """Complex type {http://www.astron.nl/SIP-Lofar}ClockType with content type SIMPLE"""
    _TypeDefinition = STD_ANON_
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ClockType')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 285, 1)
    _ElementMap = Frequency._ElementMap.copy()
    _AttributeMap = Frequency._AttributeMap.copy()
    # Base type is Frequency
    
    # Attribute units is restricted from parent
    
    # Attribute units uses Python identifier units
    __units = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'units'), 'units', '__httpwww_astron_nlSIP_Lofar_Frequency_units', _module_typeBindings.FrequencyUnit, fixed=True, unicode_default='MHz', required=True)
    __units._DeclarationLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 290, 4)
    __units._UseLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 290, 4)
    
    units = property(__units.value, __units.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __units.name() : __units
    })
_module_typeBindings.ClockType = ClockType
Namespace.addCategoryObject('typeBinding', 'ClockType', ClockType)


# Complex type {http://www.astron.nl/SIP-Lofar}ImagingPipeline with content type ELEMENT_ONLY
class ImagingPipeline (PipelineRun):
    """Complex type {http://www.astron.nl/SIP-Lofar}ImagingPipeline with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ImagingPipeline')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 599, 1)
    _ElementMap = PipelineRun._ElementMap.copy()
    _AttributeMap = PipelineRun._AttributeMap.copy()
    # Base type is PipelineRun
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName (pipelineName) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pipelineVersion (pipelineVersion) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element sourceData (sourceData) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element frequencyIntegrationStep uses Python identifier frequencyIntegrationStep
    __frequencyIntegrationStep = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep'), 'frequencyIntegrationStep', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_frequencyIntegrationStep', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 603, 5), )

    
    frequencyIntegrationStep = property(__frequencyIntegrationStep.value, __frequencyIntegrationStep.set, None, None)

    
    # Element timeIntegrationStep uses Python identifier timeIntegrationStep
    __timeIntegrationStep = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep'), 'timeIntegrationStep', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_timeIntegrationStep', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 604, 5), )

    
    timeIntegrationStep = property(__timeIntegrationStep.value, __timeIntegrationStep.set, None, None)

    
    # Element skyModelDatabase uses Python identifier skyModelDatabase
    __skyModelDatabase = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skyModelDatabase'), 'skyModelDatabase', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_skyModelDatabase', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 605, 5), )

    
    skyModelDatabase = property(__skyModelDatabase.value, __skyModelDatabase.set, None, None)

    
    # Element demixing uses Python identifier demixing
    __demixing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'demixing'), 'demixing', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_demixing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 606, 5), )

    
    demixing = property(__demixing.value, __demixing.set, None, None)

    
    # Element imagerIntegrationTime uses Python identifier imagerIntegrationTime
    __imagerIntegrationTime = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'imagerIntegrationTime'), 'imagerIntegrationTime', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_imagerIntegrationTime', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 607, 5), )

    
    imagerIntegrationTime = property(__imagerIntegrationTime.value, __imagerIntegrationTime.set, None, None)

    
    # Element numberOfMajorCycles uses Python identifier numberOfMajorCycles
    __numberOfMajorCycles = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfMajorCycles'), 'numberOfMajorCycles', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_numberOfMajorCycles', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 608, 5), )

    
    numberOfMajorCycles = property(__numberOfMajorCycles.value, __numberOfMajorCycles.set, None, None)

    
    # Element numberOfInstrumentModels uses Python identifier numberOfInstrumentModels
    __numberOfInstrumentModels = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfInstrumentModels'), 'numberOfInstrumentModels', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_numberOfInstrumentModels', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 609, 5), )

    
    numberOfInstrumentModels = property(__numberOfInstrumentModels.value, __numberOfInstrumentModels.set, None, None)

    
    # Element numberOfCorrelatedDataProducts uses Python identifier numberOfCorrelatedDataProducts
    __numberOfCorrelatedDataProducts = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), 'numberOfCorrelatedDataProducts', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_numberOfCorrelatedDataProducts', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 610, 5), )

    
    numberOfCorrelatedDataProducts = property(__numberOfCorrelatedDataProducts.value, __numberOfCorrelatedDataProducts.set, None, None)

    
    # Element numberOfSkyImages uses Python identifier numberOfSkyImages
    __numberOfSkyImages = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfSkyImages'), 'numberOfSkyImages', '__httpwww_astron_nlSIP_Lofar_ImagingPipeline_numberOfSkyImages', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 611, 5), )

    
    numberOfSkyImages = property(__numberOfSkyImages.value, __numberOfSkyImages.set, None, None)

    _ElementMap.update({
        __frequencyIntegrationStep.name() : __frequencyIntegrationStep,
        __timeIntegrationStep.name() : __timeIntegrationStep,
        __skyModelDatabase.name() : __skyModelDatabase,
        __demixing.name() : __demixing,
        __imagerIntegrationTime.name() : __imagerIntegrationTime,
        __numberOfMajorCycles.name() : __numberOfMajorCycles,
        __numberOfInstrumentModels.name() : __numberOfInstrumentModels,
        __numberOfCorrelatedDataProducts.name() : __numberOfCorrelatedDataProducts,
        __numberOfSkyImages.name() : __numberOfSkyImages
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.ImagingPipeline = ImagingPipeline
Namespace.addCategoryObject('typeBinding', 'ImagingPipeline', ImagingPipeline)


# Complex type {http://www.astron.nl/SIP-Lofar}CalibrationPipeline with content type ELEMENT_ONLY
class CalibrationPipeline (PipelineRun):
    """Complex type {http://www.astron.nl/SIP-Lofar}CalibrationPipeline with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CalibrationPipeline')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 616, 1)
    _ElementMap = PipelineRun._ElementMap.copy()
    _AttributeMap = PipelineRun._AttributeMap.copy()
    # Base type is PipelineRun
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName (pipelineName) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pipelineVersion (pipelineVersion) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element sourceData (sourceData) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element frequencyIntegrationStep uses Python identifier frequencyIntegrationStep
    __frequencyIntegrationStep = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep'), 'frequencyIntegrationStep', '__httpwww_astron_nlSIP_Lofar_CalibrationPipeline_frequencyIntegrationStep', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 620, 5), )

    
    frequencyIntegrationStep = property(__frequencyIntegrationStep.value, __frequencyIntegrationStep.set, None, None)

    
    # Element timeIntegrationStep uses Python identifier timeIntegrationStep
    __timeIntegrationStep = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep'), 'timeIntegrationStep', '__httpwww_astron_nlSIP_Lofar_CalibrationPipeline_timeIntegrationStep', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 621, 5), )

    
    timeIntegrationStep = property(__timeIntegrationStep.value, __timeIntegrationStep.set, None, None)

    
    # Element flagAutoCorrelations uses Python identifier flagAutoCorrelations
    __flagAutoCorrelations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'flagAutoCorrelations'), 'flagAutoCorrelations', '__httpwww_astron_nlSIP_Lofar_CalibrationPipeline_flagAutoCorrelations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 622, 5), )

    
    flagAutoCorrelations = property(__flagAutoCorrelations.value, __flagAutoCorrelations.set, None, None)

    
    # Element demixing uses Python identifier demixing
    __demixing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'demixing'), 'demixing', '__httpwww_astron_nlSIP_Lofar_CalibrationPipeline_demixing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 623, 5), )

    
    demixing = property(__demixing.value, __demixing.set, None, None)

    
    # Element skyModelDatabase uses Python identifier skyModelDatabase
    __skyModelDatabase = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skyModelDatabase'), 'skyModelDatabase', '__httpwww_astron_nlSIP_Lofar_CalibrationPipeline_skyModelDatabase', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 624, 5), )

    
    skyModelDatabase = property(__skyModelDatabase.value, __skyModelDatabase.set, None, None)

    
    # Element numberOfInstrumentModels uses Python identifier numberOfInstrumentModels
    __numberOfInstrumentModels = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfInstrumentModels'), 'numberOfInstrumentModels', '__httpwww_astron_nlSIP_Lofar_CalibrationPipeline_numberOfInstrumentModels', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 625, 5), )

    
    numberOfInstrumentModels = property(__numberOfInstrumentModels.value, __numberOfInstrumentModels.set, None, None)

    
    # Element numberOfCorrelatedDataProducts uses Python identifier numberOfCorrelatedDataProducts
    __numberOfCorrelatedDataProducts = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), 'numberOfCorrelatedDataProducts', '__httpwww_astron_nlSIP_Lofar_CalibrationPipeline_numberOfCorrelatedDataProducts', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 626, 5), )

    
    numberOfCorrelatedDataProducts = property(__numberOfCorrelatedDataProducts.value, __numberOfCorrelatedDataProducts.set, None, None)

    _ElementMap.update({
        __frequencyIntegrationStep.name() : __frequencyIntegrationStep,
        __timeIntegrationStep.name() : __timeIntegrationStep,
        __flagAutoCorrelations.name() : __flagAutoCorrelations,
        __demixing.name() : __demixing,
        __skyModelDatabase.name() : __skyModelDatabase,
        __numberOfInstrumentModels.name() : __numberOfInstrumentModels,
        __numberOfCorrelatedDataProducts.name() : __numberOfCorrelatedDataProducts
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CalibrationPipeline = CalibrationPipeline
Namespace.addCategoryObject('typeBinding', 'CalibrationPipeline', CalibrationPipeline)


# Complex type {http://www.astron.nl/SIP-Lofar}AveragingPipeline with content type ELEMENT_ONLY
class AveragingPipeline (PipelineRun):
    """Complex type {http://www.astron.nl/SIP-Lofar}AveragingPipeline with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AveragingPipeline')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 631, 1)
    _ElementMap = PipelineRun._ElementMap.copy()
    _AttributeMap = PipelineRun._AttributeMap.copy()
    # Base type is PipelineRun
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName (pipelineName) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pipelineVersion (pipelineVersion) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element sourceData (sourceData) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element frequencyIntegrationStep uses Python identifier frequencyIntegrationStep
    __frequencyIntegrationStep = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep'), 'frequencyIntegrationStep', '__httpwww_astron_nlSIP_Lofar_AveragingPipeline_frequencyIntegrationStep', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 635, 5), )

    
    frequencyIntegrationStep = property(__frequencyIntegrationStep.value, __frequencyIntegrationStep.set, None, None)

    
    # Element timeIntegrationStep uses Python identifier timeIntegrationStep
    __timeIntegrationStep = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep'), 'timeIntegrationStep', '__httpwww_astron_nlSIP_Lofar_AveragingPipeline_timeIntegrationStep', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 636, 5), )

    
    timeIntegrationStep = property(__timeIntegrationStep.value, __timeIntegrationStep.set, None, None)

    
    # Element flagAutoCorrelations uses Python identifier flagAutoCorrelations
    __flagAutoCorrelations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'flagAutoCorrelations'), 'flagAutoCorrelations', '__httpwww_astron_nlSIP_Lofar_AveragingPipeline_flagAutoCorrelations', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 637, 5), )

    
    flagAutoCorrelations = property(__flagAutoCorrelations.value, __flagAutoCorrelations.set, None, None)

    
    # Element demixing uses Python identifier demixing
    __demixing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'demixing'), 'demixing', '__httpwww_astron_nlSIP_Lofar_AveragingPipeline_demixing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 638, 5), )

    
    demixing = property(__demixing.value, __demixing.set, None, None)

    
    # Element numberOfCorrelatedDataProducts uses Python identifier numberOfCorrelatedDataProducts
    __numberOfCorrelatedDataProducts = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), 'numberOfCorrelatedDataProducts', '__httpwww_astron_nlSIP_Lofar_AveragingPipeline_numberOfCorrelatedDataProducts', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 639, 5), )

    
    numberOfCorrelatedDataProducts = property(__numberOfCorrelatedDataProducts.value, __numberOfCorrelatedDataProducts.set, None, None)

    _ElementMap.update({
        __frequencyIntegrationStep.name() : __frequencyIntegrationStep,
        __timeIntegrationStep.name() : __timeIntegrationStep,
        __flagAutoCorrelations.name() : __flagAutoCorrelations,
        __demixing.name() : __demixing,
        __numberOfCorrelatedDataProducts.name() : __numberOfCorrelatedDataProducts
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.AveragingPipeline = AveragingPipeline
Namespace.addCategoryObject('typeBinding', 'AveragingPipeline', AveragingPipeline)


# Complex type {http://www.astron.nl/SIP-Lofar}PulsarPipeline with content type ELEMENT_ONLY
class PulsarPipeline (PipelineRun):
    """Complex type {http://www.astron.nl/SIP-Lofar}PulsarPipeline with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PulsarPipeline')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 659, 1)
    _ElementMap = PipelineRun._ElementMap.copy()
    _AttributeMap = PipelineRun._AttributeMap.copy()
    # Base type is PipelineRun
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName (pipelineName) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pipelineVersion (pipelineVersion) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element sourceData (sourceData) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pulsarSelection uses Python identifier pulsarSelection
    __pulsarSelection = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'pulsarSelection'), 'pulsarSelection', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_pulsarSelection', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 663, 5), )

    
    pulsarSelection = property(__pulsarSelection.value, __pulsarSelection.set, None, None)

    
    # Element pulsars uses Python identifier pulsars
    __pulsars = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'pulsars'), 'pulsars', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_pulsars', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 664, 5), )

    
    pulsars = property(__pulsars.value, __pulsars.set, None, None)

    
    # Element doSinglePulseAnalysis uses Python identifier doSinglePulseAnalysis
    __doSinglePulseAnalysis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'doSinglePulseAnalysis'), 'doSinglePulseAnalysis', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_doSinglePulseAnalysis', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 665, 5), )

    
    doSinglePulseAnalysis = property(__doSinglePulseAnalysis.value, __doSinglePulseAnalysis.set, None, None)

    
    # Element convertRawTo8bit uses Python identifier convertRawTo8bit
    __convertRawTo8bit = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'convertRawTo8bit'), 'convertRawTo8bit', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_convertRawTo8bit', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 666, 5), )

    
    convertRawTo8bit = property(__convertRawTo8bit.value, __convertRawTo8bit.set, None, None)

    
    # Element subintegrationLength uses Python identifier subintegrationLength
    __subintegrationLength = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subintegrationLength'), 'subintegrationLength', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_subintegrationLength', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 667, 5), )

    
    subintegrationLength = property(__subintegrationLength.value, __subintegrationLength.set, None, None)

    
    # Element skipRFIExcision uses Python identifier skipRFIExcision
    __skipRFIExcision = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skipRFIExcision'), 'skipRFIExcision', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_skipRFIExcision', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 668, 5), )

    
    skipRFIExcision = property(__skipRFIExcision.value, __skipRFIExcision.set, None, None)

    
    # Element skipDataFolding uses Python identifier skipDataFolding
    __skipDataFolding = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skipDataFolding'), 'skipDataFolding', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_skipDataFolding', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 669, 5), )

    
    skipDataFolding = property(__skipDataFolding.value, __skipDataFolding.set, None, None)

    
    # Element skipOptimizePulsarProfile uses Python identifier skipOptimizePulsarProfile
    __skipOptimizePulsarProfile = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skipOptimizePulsarProfile'), 'skipOptimizePulsarProfile', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_skipOptimizePulsarProfile', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 670, 5), )

    
    skipOptimizePulsarProfile = property(__skipOptimizePulsarProfile.value, __skipOptimizePulsarProfile.set, None, None)

    
    # Element skipConvertRawIntoFoldedPSRFITS uses Python identifier skipConvertRawIntoFoldedPSRFITS
    __skipConvertRawIntoFoldedPSRFITS = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skipConvertRawIntoFoldedPSRFITS'), 'skipConvertRawIntoFoldedPSRFITS', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_skipConvertRawIntoFoldedPSRFITS', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 671, 5), )

    
    skipConvertRawIntoFoldedPSRFITS = property(__skipConvertRawIntoFoldedPSRFITS.value, __skipConvertRawIntoFoldedPSRFITS.set, None, None)

    
    # Element runRotationalRAdioTransientsAnalysis uses Python identifier runRotationalRAdioTransientsAnalysis
    __runRotationalRAdioTransientsAnalysis = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'runRotationalRAdioTransientsAnalysis'), 'runRotationalRAdioTransientsAnalysis', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_runRotationalRAdioTransientsAnalysis', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 672, 5), )

    
    runRotationalRAdioTransientsAnalysis = property(__runRotationalRAdioTransientsAnalysis.value, __runRotationalRAdioTransientsAnalysis.set, None, None)

    
    # Element skipDynamicSpectrum uses Python identifier skipDynamicSpectrum
    __skipDynamicSpectrum = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skipDynamicSpectrum'), 'skipDynamicSpectrum', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_skipDynamicSpectrum', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 673, 5), )

    
    skipDynamicSpectrum = property(__skipDynamicSpectrum.value, __skipDynamicSpectrum.set, None, None)

    
    # Element skipPreFold uses Python identifier skipPreFold
    __skipPreFold = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'skipPreFold'), 'skipPreFold', '__httpwww_astron_nlSIP_Lofar_PulsarPipeline_skipPreFold', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 674, 5), )

    
    skipPreFold = property(__skipPreFold.value, __skipPreFold.set, None, None)

    _ElementMap.update({
        __pulsarSelection.name() : __pulsarSelection,
        __pulsars.name() : __pulsars,
        __doSinglePulseAnalysis.name() : __doSinglePulseAnalysis,
        __convertRawTo8bit.name() : __convertRawTo8bit,
        __subintegrationLength.name() : __subintegrationLength,
        __skipRFIExcision.name() : __skipRFIExcision,
        __skipDataFolding.name() : __skipDataFolding,
        __skipOptimizePulsarProfile.name() : __skipOptimizePulsarProfile,
        __skipConvertRawIntoFoldedPSRFITS.name() : __skipConvertRawIntoFoldedPSRFITS,
        __runRotationalRAdioTransientsAnalysis.name() : __runRotationalRAdioTransientsAnalysis,
        __skipDynamicSpectrum.name() : __skipDynamicSpectrum,
        __skipPreFold.name() : __skipPreFold
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.PulsarPipeline = PulsarPipeline
Namespace.addCategoryObject('typeBinding', 'PulsarPipeline', PulsarPipeline)


# Complex type {http://www.astron.nl/SIP-Lofar}CosmicRayPipeline with content type ELEMENT_ONLY
class CosmicRayPipeline (PipelineRun):
    """Complex type {http://www.astron.nl/SIP-Lofar}CosmicRayPipeline with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CosmicRayPipeline')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 679, 1)
    _ElementMap = PipelineRun._ElementMap.copy()
    _AttributeMap = PipelineRun._AttributeMap.copy()
    # Base type is PipelineRun
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName (pipelineName) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pipelineVersion (pipelineVersion) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element sourceData (sourceData) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CosmicRayPipeline = CosmicRayPipeline
Namespace.addCategoryObject('typeBinding', 'CosmicRayPipeline', CosmicRayPipeline)


# Complex type {http://www.astron.nl/SIP-Lofar}LongBaselinePipeline with content type ELEMENT_ONLY
class LongBaselinePipeline (PipelineRun):
    """Complex type {http://www.astron.nl/SIP-Lofar}LongBaselinePipeline with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'LongBaselinePipeline')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 684, 1)
    _ElementMap = PipelineRun._ElementMap.copy()
    _AttributeMap = PipelineRun._AttributeMap.copy()
    # Base type is PipelineRun
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName (pipelineName) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pipelineVersion (pipelineVersion) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element sourceData (sourceData) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element subbandsPerSubbandGroup uses Python identifier subbandsPerSubbandGroup
    __subbandsPerSubbandGroup = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subbandsPerSubbandGroup'), 'subbandsPerSubbandGroup', '__httpwww_astron_nlSIP_Lofar_LongBaselinePipeline_subbandsPerSubbandGroup', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 688, 5), )

    
    subbandsPerSubbandGroup = property(__subbandsPerSubbandGroup.value, __subbandsPerSubbandGroup.set, None, None)

    
    # Element subbandGroupsPerMS uses Python identifier subbandGroupsPerMS
    __subbandGroupsPerMS = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'subbandGroupsPerMS'), 'subbandGroupsPerMS', '__httpwww_astron_nlSIP_Lofar_LongBaselinePipeline_subbandGroupsPerMS', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 689, 5), )

    
    subbandGroupsPerMS = property(__subbandGroupsPerMS.value, __subbandGroupsPerMS.set, None, None)

    _ElementMap.update({
        __subbandsPerSubbandGroup.name() : __subbandsPerSubbandGroup,
        __subbandGroupsPerMS.name() : __subbandGroupsPerMS
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.LongBaselinePipeline = LongBaselinePipeline
Namespace.addCategoryObject('typeBinding', 'LongBaselinePipeline', LongBaselinePipeline)


# Complex type {http://www.astron.nl/SIP-Lofar}GenericPipeline with content type ELEMENT_ONLY
class GenericPipeline (PipelineRun):
    """Complex type {http://www.astron.nl/SIP-Lofar}GenericPipeline with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'GenericPipeline')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 694, 1)
    _ElementMap = PipelineRun._ElementMap.copy()
    _AttributeMap = PipelineRun._AttributeMap.copy()
    # Base type is PipelineRun
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element observationId (observationId) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element parset (parset) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyName (strategyName) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element strategyDescription (strategyDescription) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element startTime (startTime) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element duration (duration) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element relations (relations) inherited from {http://www.astron.nl/SIP-Lofar}Process
    
    # Element pipelineName (pipelineName) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element pipelineVersion (pipelineVersion) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    
    # Element sourceData (sourceData) inherited from {http://www.astron.nl/SIP-Lofar}PipelineRun
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.GenericPipeline = GenericPipeline
Namespace.addCategoryObject('typeBinding', 'GenericPipeline', GenericPipeline)


# Complex type {http://www.astron.nl/SIP-Lofar}SkyImageDataProduct with content type ELEMENT_ONLY
class SkyImageDataProduct (PixelMapDataProduct):
    """Complex type {http://www.astron.nl/SIP-Lofar}SkyImageDataProduct with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SkyImageDataProduct')
    _XSDLocation = pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1147, 1)
    _ElementMap = PixelMapDataProduct._ElementMap.copy()
    _AttributeMap = PixelMapDataProduct._AttributeMap.copy()
    # Base type is PixelMapDataProduct
    
    # Element dataProductType (dataProductType) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element dataProductIdentifier (dataProductIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element storageTicket (storageTicket) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element size (size) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element checksum (checksum) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileName (fileName) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element fileFormat (fileFormat) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element processIdentifier (processIdentifier) inherited from {http://www.astron.nl/SIP-Lofar}DataProduct
    
    # Element numberOfAxes (numberOfAxes) inherited from {http://www.astron.nl/SIP-Lofar}PixelMapDataProduct
    
    # Element numberOfCoordinates (numberOfCoordinates) inherited from {http://www.astron.nl/SIP-Lofar}PixelMapDataProduct
    
    # Element coordinate (coordinate) inherited from {http://www.astron.nl/SIP-Lofar}PixelMapDataProduct
    
    # Element locationFrame uses Python identifier locationFrame
    __locationFrame = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'locationFrame'), 'locationFrame', '__httpwww_astron_nlSIP_Lofar_SkyImageDataProduct_locationFrame', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1151, 5), )

    
    locationFrame = property(__locationFrame.value, __locationFrame.set, None, None)

    
    # Element timeFrame uses Python identifier timeFrame
    __timeFrame = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'timeFrame'), 'timeFrame', '__httpwww_astron_nlSIP_Lofar_SkyImageDataProduct_timeFrame', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1152, 5), )

    
    timeFrame = property(__timeFrame.value, __timeFrame.set, None, None)

    
    # Element observationPointing uses Python identifier observationPointing
    __observationPointing = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'observationPointing'), 'observationPointing', '__httpwww_astron_nlSIP_Lofar_SkyImageDataProduct_observationPointing', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1153, 5), )

    
    observationPointing = property(__observationPointing.value, __observationPointing.set, None, None)

    
    # Element restoringBeamMajor uses Python identifier restoringBeamMajor
    __restoringBeamMajor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'restoringBeamMajor'), 'restoringBeamMajor', '__httpwww_astron_nlSIP_Lofar_SkyImageDataProduct_restoringBeamMajor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1154, 5), )

    
    restoringBeamMajor = property(__restoringBeamMajor.value, __restoringBeamMajor.set, None, None)

    
    # Element restoringBeamMinor uses Python identifier restoringBeamMinor
    __restoringBeamMinor = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'restoringBeamMinor'), 'restoringBeamMinor', '__httpwww_astron_nlSIP_Lofar_SkyImageDataProduct_restoringBeamMinor', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1155, 5), )

    
    restoringBeamMinor = property(__restoringBeamMinor.value, __restoringBeamMinor.set, None, None)

    
    # Element rmsNoise uses Python identifier rmsNoise
    __rmsNoise = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'rmsNoise'), 'rmsNoise', '__httpwww_astron_nlSIP_Lofar_SkyImageDataProduct_rmsNoise', False, pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1156, 5), )

    
    rmsNoise = property(__rmsNoise.value, __rmsNoise.set, None, None)

    _ElementMap.update({
        __locationFrame.name() : __locationFrame,
        __timeFrame.name() : __timeFrame,
        __observationPointing.name() : __observationPointing,
        __restoringBeamMajor.name() : __restoringBeamMajor,
        __restoringBeamMinor.name() : __restoringBeamMinor,
        __rmsNoise.name() : __rmsNoise
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.SkyImageDataProduct = SkyImageDataProduct
Namespace.addCategoryObject('typeBinding', 'SkyImageDataProduct', SkyImageDataProduct)


ltaSip = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ltaSip'), LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1206, 1))
Namespace.addCategoryObject('elementBinding', ltaSip.name().localName(), ltaSip)



ListOfFrequencies._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'frequencies'), ListOfDouble, scope=ListOfFrequencies, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 104, 3)))

ListOfFrequencies._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'unit'), FrequencyUnit, scope=ListOfFrequencies, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 105, 3)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ListOfFrequencies._UseForTag(pyxb.namespace.ExpandedName(None, 'frequencies')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 104, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ListOfFrequencies._UseForTag(pyxb.namespace.ExpandedName(None, 'unit')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 105, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ListOfFrequencies._Automaton = _BuildAutomaton()




IdentifierType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'source'), pyxb.binding.datatypes.string, scope=IdentifierType, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 114, 3)))

IdentifierType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'identifier'), pyxb.binding.datatypes.nonNegativeInteger, scope=IdentifierType, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 115, 3)))

IdentifierType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'name'), pyxb.binding.datatypes.string, scope=IdentifierType, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 116, 3)))

IdentifierType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'label'), pyxb.binding.datatypes.string, scope=IdentifierType, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 117, 12)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 116, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 117, 12))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IdentifierType._UseForTag(pyxb.namespace.ExpandedName(None, 'source')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 114, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IdentifierType._UseForTag(pyxb.namespace.ExpandedName(None, 'identifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 115, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(IdentifierType._UseForTag(pyxb.namespace.ExpandedName(None, 'name')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 116, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(IdentifierType._UseForTag(pyxb.namespace.ExpandedName(None, 'label')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 117, 12))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
IdentifierType._Automaton = _BuildAutomaton_()




Pointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'rightAscension'), Angle, scope=Pointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 134, 4)))

Pointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'azimuth'), Angle, scope=Pointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 135, 4)))

Pointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'declination'), Angle, scope=Pointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 138, 4)))

Pointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'altitude'), Angle, scope=Pointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 139, 4)))

Pointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'equinox'), EquinoxType, scope=Pointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 141, 3)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Pointing._UseForTag(pyxb.namespace.ExpandedName(None, 'rightAscension')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 134, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Pointing._UseForTag(pyxb.namespace.ExpandedName(None, 'azimuth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 135, 4))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Pointing._UseForTag(pyxb.namespace.ExpandedName(None, 'declination')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 138, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Pointing._UseForTag(pyxb.namespace.ExpandedName(None, 'altitude')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 139, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Pointing._UseForTag(pyxb.namespace.ExpandedName(None, 'equinox')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 141, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Pointing._Automaton = _BuildAutomaton_2()




Coordinates._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'coordinateSystem'), STD_ANON, scope=Coordinates, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 157, 3)))

Coordinates._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'x'), Length, scope=Coordinates, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 168, 5)))

Coordinates._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'y'), Length, scope=Coordinates, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 169, 5)))

Coordinates._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'z'), Length, scope=Coordinates, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 170, 5)))

Coordinates._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'radius'), Length, scope=Coordinates, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 173, 5)))

Coordinates._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'longitude'), Angle, scope=Coordinates, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 174, 5)))

Coordinates._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'latitude'), Angle, scope=Coordinates, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 175, 5)))

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Coordinates._UseForTag(pyxb.namespace.ExpandedName(None, 'coordinateSystem')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 157, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Coordinates._UseForTag(pyxb.namespace.ExpandedName(None, 'x')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 168, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Coordinates._UseForTag(pyxb.namespace.ExpandedName(None, 'y')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 169, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Coordinates._UseForTag(pyxb.namespace.ExpandedName(None, 'z')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 170, 5))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Coordinates._UseForTag(pyxb.namespace.ExpandedName(None, 'radius')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 173, 5))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Coordinates._UseForTag(pyxb.namespace.ExpandedName(None, 'longitude')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 174, 5))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Coordinates._UseForTag(pyxb.namespace.ExpandedName(None, 'latitude')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 175, 5))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    st_6._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Coordinates._Automaton = _BuildAutomaton_3()




AntennaField._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'name'), AntennaFieldType, scope=AntennaField, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 206, 3)))

AntennaField._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'location'), Coordinates, scope=AntennaField, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 207, 3)))

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AntennaField._UseForTag(pyxb.namespace.ExpandedName(None, 'name')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 206, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AntennaField._UseForTag(pyxb.namespace.ExpandedName(None, 'location')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 207, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
AntennaField._Automaton = _BuildAutomaton_4()




Stations._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'station'), Station, scope=Stations, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 212, 3)))

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Stations._UseForTag(pyxb.namespace.ExpandedName(None, 'station')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 212, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Stations._Automaton = _BuildAutomaton_5()




Station._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'name'), pyxb.binding.datatypes.string, scope=Station, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 220, 3)))

Station._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stationType'), StationTypeType, scope=Station, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 221, 3)))

Station._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'antennaField'), AntennaField, scope=Station, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 222, 3)))

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=2, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 222, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Station._UseForTag(pyxb.namespace.ExpandedName(None, 'name')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 220, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Station._UseForTag(pyxb.namespace.ExpandedName(None, 'stationType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 221, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(Station._UseForTag(pyxb.namespace.ExpandedName(None, 'antennaField')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 222, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Station._Automaton = _BuildAutomaton_6()




ProcessRelation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'relationType'), ProcessRelationType, scope=ProcessRelation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 246, 3)))

ProcessRelation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'identifier'), IdentifierType, scope=ProcessRelation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 247, 3)))

ProcessRelation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'name'), pyxb.binding.datatypes.string, scope=ProcessRelation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 248, 3)))

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 248, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ProcessRelation._UseForTag(pyxb.namespace.ExpandedName(None, 'relationType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 246, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ProcessRelation._UseForTag(pyxb.namespace.ExpandedName(None, 'identifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 247, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ProcessRelation._UseForTag(pyxb.namespace.ExpandedName(None, 'name')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 248, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ProcessRelation._Automaton = _BuildAutomaton_7()




ProcessRelations._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'relation'), ProcessRelation, scope=ProcessRelations, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 253, 3)))

def _BuildAutomaton_8 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 253, 3))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ProcessRelations._UseForTag(pyxb.namespace.ExpandedName(None, 'relation')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 253, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
ProcessRelations._Automaton = _BuildAutomaton_8()




Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'processIdentifier'), IdentifierType, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3)))

Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observationId'), IdentifierType, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3)))

Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'parset'), IdentifierType, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3)))

Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'strategyName'), pyxb.binding.datatypes.string, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3)))

Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'strategyDescription'), pyxb.binding.datatypes.string, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3)))

Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'startTime'), pyxb.binding.datatypes.dateTime, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3)))

Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'duration'), pyxb.binding.datatypes.duration, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3)))

Process._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'relations'), ProcessRelations, scope=Process, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3)))

def _BuildAutomaton_9 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Process._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Process._Automaton = _BuildAutomaton_9()




Processing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'correlator'), Correlator, scope=Processing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 441, 3)))

Processing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'coherentStokes'), CoherentStokes, scope=Processing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 442, 3)))

Processing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'incoherentStokes'), IncoherentStokes, scope=Processing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 443, 3)))

Processing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'flysEye'), FlysEye, scope=Processing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 444, 3)))

Processing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'nonStandard'), NonStandard, scope=Processing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 445, 3)))

def _BuildAutomaton_10 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 441, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 442, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 443, 3))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 444, 3))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 445, 3))
    counters.add(cc_4)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(Processing._UseForTag(pyxb.namespace.ExpandedName(None, 'correlator')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 441, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(Processing._UseForTag(pyxb.namespace.ExpandedName(None, 'coherentStokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 442, 3))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(Processing._UseForTag(pyxb.namespace.ExpandedName(None, 'incoherentStokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 443, 3))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(Processing._UseForTag(pyxb.namespace.ExpandedName(None, 'flysEye')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 444, 3))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(Processing._UseForTag(pyxb.namespace.ExpandedName(None, 'nonStandard')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 445, 3))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
Processing._Automaton = _BuildAutomaton_10()




RealTimeProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'processingType'), ProcessingType, scope=RealTimeProcess, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3)))

def _BuildAutomaton_11 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RealTimeProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'processingType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
RealTimeProcess._Automaton = _BuildAutomaton_11()




TransientBufferBoardEvents._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'transientBufferBoardEvent'), TransientBufferBoardEvent, scope=TransientBufferBoardEvents, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 536, 3)))

def _BuildAutomaton_12 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_12
    del _BuildAutomaton_12
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardEvents._UseForTag(pyxb.namespace.ExpandedName(None, 'transientBufferBoardEvent')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 536, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TransientBufferBoardEvents._Automaton = _BuildAutomaton_12()




TransientBufferBoardEvent._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'eventSource'), pyxb.binding.datatypes.string, scope=TransientBufferBoardEvent, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 541, 3)))

def _BuildAutomaton_13 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_13
    del _BuildAutomaton_13
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardEvent._UseForTag(pyxb.namespace.ExpandedName(None, 'eventSource')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 541, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TransientBufferBoardEvent._Automaton = _BuildAutomaton_13()




SubArrayPointings._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subArrayPointing'), SubArrayPointing, scope=SubArrayPointings, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 546, 3)))

def _BuildAutomaton_14 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_14
    del _BuildAutomaton_14
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SubArrayPointings._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 546, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SubArrayPointings._Automaton = _BuildAutomaton_14()




SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'pointing'), Pointing, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 559, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'beamNumber'), pyxb.binding.datatypes.unsignedShort, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 560, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'measurementDescription'), pyxb.binding.datatypes.string, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 561, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier'), IdentifierType, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 562, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'measurementType'), MeasurementType, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 563, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'targetName'), pyxb.binding.datatypes.string, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 564, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'startTime'), pyxb.binding.datatypes.dateTime, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 565, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'duration'), pyxb.binding.datatypes.duration, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 566, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfProcessing'), pyxb.binding.datatypes.unsignedShort, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 567, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'processing'), Processing, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 568, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), pyxb.binding.datatypes.unsignedShort, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 569, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfBeamFormedDataProducts'), pyxb.binding.datatypes.unsignedShort, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 570, 3)))

SubArrayPointing._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'relations'), ProcessRelations, scope=SubArrayPointing, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 571, 3)))

def _BuildAutomaton_15 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_15
    del _BuildAutomaton_15
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 561, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 568, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'pointing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 559, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'beamNumber')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 560, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'measurementDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 561, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 562, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'measurementType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 563, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'targetName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 564, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 565, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 566, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfProcessing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 567, 3))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'processing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 568, 3))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 569, 3))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfBeamFormedDataProducts')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 570, 3))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SubArrayPointing._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 571, 3))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    st_12._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SubArrayPointing._Automaton = _BuildAutomaton_15()




DataSources._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier'), IdentifierType, scope=DataSources, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 582, 3)))

def _BuildAutomaton_16 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_16
    del _BuildAutomaton_16
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DataSources._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 582, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
DataSources._Automaton = _BuildAutomaton_16()




ChecksumType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'algorithm'), ChecksumAlgorithm, scope=ChecksumType, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 730, 3)))

ChecksumType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'value'), pyxb.binding.datatypes.string, scope=ChecksumType, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 731, 3)))

def _BuildAutomaton_17 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_17
    del _BuildAutomaton_17
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ChecksumType._UseForTag(pyxb.namespace.ExpandedName(None, 'algorithm')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 730, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ChecksumType._UseForTag(pyxb.namespace.ExpandedName(None, 'value')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 731, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ChecksumType._Automaton = _BuildAutomaton_17()




TBBTrigger._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'type'), pyxb.binding.datatypes.string, scope=TBBTrigger, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 757, 3)))

TBBTrigger._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'value'), pyxb.binding.datatypes.string, scope=TBBTrigger, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 758, 3)))

def _BuildAutomaton_18 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_18
    del _BuildAutomaton_18
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TBBTrigger._UseForTag(pyxb.namespace.ExpandedName(None, 'type')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 757, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TBBTrigger._UseForTag(pyxb.namespace.ExpandedName(None, 'value')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 758, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TBBTrigger._Automaton = _BuildAutomaton_18()




DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'dataProductType'), DataProductType, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3)))

DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier'), IdentifierType, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3)))

DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'storageTicket'), pyxb.binding.datatypes.string, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3)))

DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'size'), pyxb.binding.datatypes.unsignedLong, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3)))

DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'checksum'), ChecksumType, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3)))

DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'fileName'), pyxb.binding.datatypes.string, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3)))

DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'fileFormat'), FileFormatType, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3)))

DataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'processIdentifier'), IdentifierType, scope=DataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3)))

def _BuildAutomaton_19 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_19
    del _BuildAutomaton_19
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
DataProduct._Automaton = _BuildAutomaton_19()




ArrayBeams._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'arrayBeam'), ArrayBeam, scope=ArrayBeams, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 871, 3)))

def _BuildAutomaton_20 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_20
    del _BuildAutomaton_20
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ArrayBeams._UseForTag(pyxb.namespace.ExpandedName(None, 'arrayBeam')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 871, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
         ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ArrayBeams._Automaton = _BuildAutomaton_20()




ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier'), IdentifierType, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 879, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'beamNumber'), pyxb.binding.datatypes.unsignedShort, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 880, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'dispersionMeasure'), pyxb.binding.datatypes.double, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 881, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfSubbands'), pyxb.binding.datatypes.unsignedShort, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 882, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stationSubbands'), ListOfSubbands, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 883, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'samplingTime'), Time, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 884, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'centralFrequencies'), ListOfFrequencies, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 885, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 886, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 887, 3)))

ArrayBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stokes'), PolarizationType, scope=ArrayBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3)))

def _BuildAutomaton_21 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_21
    del _BuildAutomaton_21
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 879, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'beamNumber')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 880, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'dispersionMeasure')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 881, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 882, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stationSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 883, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'samplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 884, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'centralFrequencies')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 885, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 886, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 887, 3))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ArrayBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ArrayBeam._Automaton = _BuildAutomaton_21()




Axis._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'number'), pyxb.binding.datatypes.unsignedShort, scope=Axis, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 996, 3)))

Axis._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'name'), pyxb.binding.datatypes.string, scope=Axis, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 997, 3)))

Axis._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'units'), pyxb.binding.datatypes.string, scope=Axis, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 998, 3)))

Axis._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'length'), pyxb.binding.datatypes.unsignedInt, scope=Axis, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 999, 3)))

def _BuildAutomaton_22 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_22
    del _BuildAutomaton_22
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Axis._UseForTag(pyxb.namespace.ExpandedName(None, 'number')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 996, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Axis._UseForTag(pyxb.namespace.ExpandedName(None, 'name')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 997, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Axis._UseForTag(pyxb.namespace.ExpandedName(None, 'units')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 998, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Axis._UseForTag(pyxb.namespace.ExpandedName(None, 'length')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 999, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Axis._Automaton = _BuildAutomaton_22()




SpectralQuantity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'type'), SpectralQuantityType, scope=SpectralQuantity, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1083, 3)))

SpectralQuantity._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'value'), pyxb.binding.datatypes.double, scope=SpectralQuantity, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1084, 3)))

def _BuildAutomaton_23 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_23
    del _BuildAutomaton_23
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SpectralQuantity._UseForTag(pyxb.namespace.ExpandedName(None, 'type')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1083, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SpectralQuantity._UseForTag(pyxb.namespace.ExpandedName(None, 'value')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1084, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SpectralQuantity._Automaton = _BuildAutomaton_23()




Parset._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'identifier'), IdentifierType, scope=Parset, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1170, 3)))

Parset._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'contents'), pyxb.binding.datatypes.string, scope=Parset, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1171, 3)))

def _BuildAutomaton_24 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_24
    del _BuildAutomaton_24
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Parset._UseForTag(pyxb.namespace.ExpandedName(None, 'identifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1170, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Parset._UseForTag(pyxb.namespace.ExpandedName(None, 'contents')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1171, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Parset._Automaton = _BuildAutomaton_24()




Project._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'projectCode'), pyxb.binding.datatypes.string, scope=Project, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1191, 3)))

Project._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'primaryInvestigator'), pyxb.binding.datatypes.string, scope=Project, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1192, 3)))

Project._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'coInvestigator'), pyxb.binding.datatypes.string, scope=Project, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1193, 3)))

Project._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'contactAuthor'), pyxb.binding.datatypes.string, scope=Project, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1194, 3)))

Project._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'telescope'), Telescope, scope=Project, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1195, 3)))

Project._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'projectDescription'), pyxb.binding.datatypes.string, scope=Project, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1196, 3)))

def _BuildAutomaton_25 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_25
    del _BuildAutomaton_25
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1193, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Project._UseForTag(pyxb.namespace.ExpandedName(None, 'projectCode')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1191, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Project._UseForTag(pyxb.namespace.ExpandedName(None, 'primaryInvestigator')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1192, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Project._UseForTag(pyxb.namespace.ExpandedName(None, 'coInvestigator')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1193, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Project._UseForTag(pyxb.namespace.ExpandedName(None, 'contactAuthor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1194, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Project._UseForTag(pyxb.namespace.ExpandedName(None, 'telescope')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1195, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Project._UseForTag(pyxb.namespace.ExpandedName(None, 'projectDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1196, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Project._Automaton = _BuildAutomaton_25()




LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'sipGeneratorVersion'), pyxb.binding.datatypes.string, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1209, 3)))

LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'project'), Project, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1210, 3)))

LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'dataProduct'), DataProduct, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1211, 3)))

LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observation'), Observation, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1212, 3)))

LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'pipelineRun'), PipelineRun, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1213, 3)))

LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'unspecifiedProcess'), UnspecifiedProcess, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1214, 3)))

LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'relatedDataProduct'), DataProduct, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1215, 3)))

LTASip._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'parset'), Parset, scope=LTASip, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1216, 3)))

def _BuildAutomaton_26 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_26
    del _BuildAutomaton_26
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1212, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1213, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1214, 3))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1215, 3))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1216, 3))
    counters.add(cc_4)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'sipGeneratorVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1209, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'project')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1210, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProduct')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1211, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'observation')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1212, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineRun')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1213, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'unspecifiedProcess')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1214, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'relatedDataProduct')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1215, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(LTASip._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1216, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    transitions.append(fac.Transition(st_7, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_4, True) ]))
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
LTASip._Automaton = _BuildAutomaton_26()




Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observingMode'), ObservingModeType, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 354, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observationDescription'), pyxb.binding.datatypes.string, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 355, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'instrumentFilter'), FilterSelectionType, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 356, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'clock'), ClockType, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 357, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stationSelection'), StationSelectionType, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 358, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'antennaSet'), AntennaSetType, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 359, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeSystem'), TimeSystemType, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 360, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 361, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 362, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfStations'), pyxb.binding.datatypes.unsignedByte, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 363, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stations'), Stations, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 364, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfSubArrayPointings'), pyxb.binding.datatypes.unsignedShort, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 365, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subArrayPointings'), SubArrayPointings, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 366, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOftransientBufferBoardEvents'), pyxb.binding.datatypes.unsignedShort, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 367, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'transientBufferBoardEvents'), TransientBufferBoardEvents, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 368, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), pyxb.binding.datatypes.unsignedShort, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 369, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfBeamFormedDataProducts'), pyxb.binding.datatypes.unsignedShort, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 370, 5)))

Observation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfBitsPerSample'), pyxb.binding.datatypes.unsignedShort, scope=Observation, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 371, 5)))

def _BuildAutomaton_27 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_27
    del _BuildAutomaton_27
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 355, 5))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 361, 5))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 362, 5))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 366, 5))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 368, 5))
    counters.add(cc_5)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'observingMode')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 354, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'observationDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 355, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'instrumentFilter')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 356, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'clock')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 357, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'stationSelection')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 358, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'antennaSet')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 359, 5))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'timeSystem')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 360, 5))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 361, 5))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 362, 5))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfStations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 363, 5))
    st_17 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'stations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 364, 5))
    st_18 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_18)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfSubArrayPointings')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 365, 5))
    st_19 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_19)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointings')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 366, 5))
    st_20 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_20)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOftransientBufferBoardEvents')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 367, 5))
    st_21 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_21)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'transientBufferBoardEvents')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 368, 5))
    st_22 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_22)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 369, 5))
    st_23 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_23)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfBeamFormedDataProducts')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 370, 5))
    st_24 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_24)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Observation._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfBitsPerSample')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 371, 5))
    st_25 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_25)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
         ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
         ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
         ]))
    transitions.append(fac.Transition(st_16, [
         ]))
    transitions.append(fac.Transition(st_17, [
         ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_17, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_18, [
         ]))
    st_17._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_19, [
         ]))
    st_18._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_20, [
         ]))
    transitions.append(fac.Transition(st_21, [
         ]))
    st_19._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_20, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_21, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_20._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_22, [
         ]))
    transitions.append(fac.Transition(st_23, [
         ]))
    st_21._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_22, [
        fac.UpdateInstruction(cc_5, True) ]))
    transitions.append(fac.Transition(st_23, [
        fac.UpdateInstruction(cc_5, False) ]))
    st_22._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_24, [
         ]))
    st_23._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_25, [
         ]))
    st_24._set_transitionSet(transitions)
    transitions = []
    st_25._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Observation._Automaton = _BuildAutomaton_27()




DirectDataMeasurement._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observingMode'), ObservingModeType, scope=DirectDataMeasurement, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 380, 5)))

DirectDataMeasurement._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'station'), Station, scope=DirectDataMeasurement, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 381, 5)))

def _BuildAutomaton_28 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_28
    del _BuildAutomaton_28
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'observingMode')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 380, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DirectDataMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'station')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 381, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
DirectDataMeasurement._Automaton = _BuildAutomaton_28()




GenericMeasurement._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observingMode'), ObservingModeType, scope=GenericMeasurement, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 397, 5)))

GenericMeasurement._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'description'), pyxb.binding.datatypes.string, scope=GenericMeasurement, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 398, 5)))

def _BuildAutomaton_29 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_29
    del _BuildAutomaton_29
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'observingMode')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 397, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GenericMeasurement._UseForTag(pyxb.namespace.ExpandedName(None, 'description')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 398, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
GenericMeasurement._Automaton = _BuildAutomaton_29()




UnspecifiedProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observingMode'), ObservingModeType, scope=UnspecifiedProcess, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 407, 5)))

UnspecifiedProcess._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'description'), pyxb.binding.datatypes.string, scope=UnspecifiedProcess, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 408, 5)))

def _BuildAutomaton_30 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_30
    del _BuildAutomaton_30
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'observingMode')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 407, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnspecifiedProcess._UseForTag(pyxb.namespace.ExpandedName(None, 'description')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 408, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
UnspecifiedProcess._Automaton = _BuildAutomaton_30()




Correlator._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'integrationInterval'), Time, scope=Correlator, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 457, 5)))

Correlator._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=Correlator, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 458, 5)))

Correlator._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=Correlator, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 459, 5)))

def _BuildAutomaton_31 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_31
    del _BuildAutomaton_31
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 458, 5))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 459, 5))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(Correlator._UseForTag(pyxb.namespace.ExpandedName(None, 'processingType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(Correlator._UseForTag(pyxb.namespace.ExpandedName(None, 'integrationInterval')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 457, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(Correlator._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 458, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(Correlator._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 459, 5))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
Correlator._Automaton = _BuildAutomaton_31()




CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'rawSamplingTime'), Time, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 478, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor'), pyxb.binding.datatypes.unsignedInt, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 479, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'samplingTime'), Time, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 480, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'frequencyDownsamplingFactor'), pyxb.binding.datatypes.unsignedShort, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 481, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCollapsedChannels'), pyxb.binding.datatypes.unsignedShort, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 482, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stokes'), PolarizationType, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 483, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfStations'), pyxb.binding.datatypes.unsignedByte, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 484, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stations'), Stations, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 485, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 486, 5)))

CoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=CoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 487, 5)))

def _BuildAutomaton_32 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_32
    del _BuildAutomaton_32
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 481, 5))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 482, 5))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 483, 5))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 486, 5))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 487, 5))
    counters.add(cc_4)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'processingType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'rawSamplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 478, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 479, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'samplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 480, 5))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'frequencyDownsamplingFactor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 481, 5))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCollapsedChannels')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 482, 5))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'stokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 483, 5))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfStations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 484, 5))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'stations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 485, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 486, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(CoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 487, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_4, True) ]))
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CoherentStokes._Automaton = _BuildAutomaton_32()




IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'rawSamplingTime'), Time, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 496, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor'), pyxb.binding.datatypes.unsignedInt, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 497, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'samplingTime'), Time, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 498, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'frequencyDownsamplingFactor'), pyxb.binding.datatypes.unsignedShort, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 499, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCollapsedChannels'), pyxb.binding.datatypes.unsignedShort, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 500, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stokes'), PolarizationType, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 501, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfStations'), pyxb.binding.datatypes.unsignedByte, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 502, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stations'), Stations, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 503, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 504, 5)))

IncoherentStokes._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=IncoherentStokes, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 505, 5)))

def _BuildAutomaton_33 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_33
    del _BuildAutomaton_33
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 499, 5))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 500, 5))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 501, 5))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 504, 5))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 505, 5))
    counters.add(cc_4)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'processingType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'rawSamplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 496, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 497, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'samplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 498, 5))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'frequencyDownsamplingFactor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 499, 5))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCollapsedChannels')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 500, 5))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'stokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 501, 5))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfStations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 502, 5))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'stations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 503, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 504, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(IncoherentStokes._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 505, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    transitions.append(fac.Transition(st_6, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_7, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    transitions.append(fac.Transition(st_10, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_4, True) ]))
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
IncoherentStokes._Automaton = _BuildAutomaton_33()




FlysEye._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'rawSamplingTime'), Time, scope=FlysEye, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 514, 5)))

FlysEye._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor'), pyxb.binding.datatypes.unsignedInt, scope=FlysEye, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 515, 5)))

FlysEye._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'samplingTime'), Time, scope=FlysEye, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 516, 5)))

FlysEye._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stokes'), PolarizationType, scope=FlysEye, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 517, 5)))

FlysEye._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=FlysEye, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 518, 5)))

FlysEye._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=FlysEye, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 519, 5)))

def _BuildAutomaton_34 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_34
    del _BuildAutomaton_34
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 517, 5))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 518, 5))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 519, 5))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEye._UseForTag(pyxb.namespace.ExpandedName(None, 'processingType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEye._UseForTag(pyxb.namespace.ExpandedName(None, 'rawSamplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 514, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEye._UseForTag(pyxb.namespace.ExpandedName(None, 'timeDownsamplingFactor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 515, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEye._UseForTag(pyxb.namespace.ExpandedName(None, 'samplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 516, 5))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(FlysEye._UseForTag(pyxb.namespace.ExpandedName(None, 'stokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 517, 5))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(FlysEye._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 518, 5))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(FlysEye._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 519, 5))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_6._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
FlysEye._Automaton = _BuildAutomaton_34()




NonStandard._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=NonStandard, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 528, 5)))

NonStandard._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=NonStandard, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 529, 5)))

def _BuildAutomaton_35 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_35
    del _BuildAutomaton_35
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(NonStandard._UseForTag(pyxb.namespace.ExpandedName(None, 'processingType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 450, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(NonStandard._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 528, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(NonStandard._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 529, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
NonStandard._Automaton = _BuildAutomaton_35()




PipelineRun._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'pipelineName'), pyxb.binding.datatypes.string, scope=PipelineRun, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5)))

PipelineRun._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'pipelineVersion'), pyxb.binding.datatypes.string, scope=PipelineRun, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5)))

PipelineRun._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'sourceData'), DataSources, scope=PipelineRun, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5)))

def _BuildAutomaton_36 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_36
    del _BuildAutomaton_36
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PipelineRun._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PipelineRun._Automaton = _BuildAutomaton_36()




CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier'), IdentifierType, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 812, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subband'), pyxb.binding.datatypes.unsignedShort, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 813, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'stationSubband'), pyxb.binding.datatypes.unsignedShort, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 814, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'startTime'), pyxb.binding.datatypes.dateTime, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 815, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'duration'), pyxb.binding.datatypes.duration, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 816, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'integrationInterval'), Time, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 817, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'centralFrequency'), Frequency, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 818, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelWidth'), Frequency, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 819, 5)))

CorrelatedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'channelsPerSubband'), pyxb.binding.datatypes.unsignedShort, scope=CorrelatedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 820, 5)))

def _BuildAutomaton_37 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_37
    del _BuildAutomaton_37
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 814, 5))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 812, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'subband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 813, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'stationSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 814, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 815, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 816, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'integrationInterval')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 817, 5))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'centralFrequency')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 818, 5))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 819, 5))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CorrelatedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 820, 5))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    transitions.append(fac.Transition(st_11, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
         ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
         ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
         ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
         ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    st_16._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CorrelatedDataProduct._Automaton = _BuildAutomaton_37()




def _BuildAutomaton_38 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_38
    del _BuildAutomaton_38
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(InstrumentModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
InstrumentModelDataProduct._Automaton = _BuildAutomaton_38()




def _BuildAutomaton_39 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_39
    del _BuildAutomaton_39
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SkyModelDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SkyModelDataProduct._Automaton = _BuildAutomaton_39()




TransientBufferBoardDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfSamples'), pyxb.binding.datatypes.unsignedInt, scope=TransientBufferBoardDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 855, 5)))

TransientBufferBoardDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeStamp'), pyxb.binding.datatypes.unsignedInt, scope=TransientBufferBoardDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 856, 5)))

TransientBufferBoardDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'triggerParameters'), TBBTrigger, scope=TransientBufferBoardDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 857, 5)))

def _BuildAutomaton_40 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_40
    del _BuildAutomaton_40
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfSamples')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 855, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'timeStamp')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 856, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TransientBufferBoardDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'triggerParameters')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 857, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TransientBufferBoardDataProduct._Automaton = _BuildAutomaton_40()




CoherentStokesBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'pointing'), Pointing, scope=CoherentStokesBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 900, 5)))

CoherentStokesBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'offset'), Pointing, scope=CoherentStokesBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 901, 5)))

def _BuildAutomaton_41 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_41
    del _BuildAutomaton_41
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 879, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'beamNumber')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 880, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'dispersionMeasure')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 881, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 882, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stationSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 883, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'samplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 884, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'centralFrequencies')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 885, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 886, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 887, 3))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'pointing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 900, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'offset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 901, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    st_11._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CoherentStokesBeam._Automaton = _BuildAutomaton_41()




def _BuildAutomaton_42 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_42
    del _BuildAutomaton_42
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 879, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'beamNumber')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 880, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'dispersionMeasure')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 881, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 882, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stationSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 883, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'samplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 884, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'centralFrequencies')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 885, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 886, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 887, 3))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(IncoherentStokesBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
IncoherentStokesBeam._Automaton = _BuildAutomaton_42()




FlysEyeBeam._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'station'), Station, scope=FlysEyeBeam, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 917, 5)))

def _BuildAutomaton_43 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_43
    del _BuildAutomaton_43
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'subArrayPointingIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 879, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'beamNumber')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 880, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'dispersionMeasure')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 881, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 882, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stationSubbands')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 883, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'samplingTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 884, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'centralFrequencies')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 885, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelWidth')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 886, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'channelsPerSubband')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 887, 3))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'stokes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 888, 3))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(FlysEyeBeam._UseForTag(pyxb.namespace.ExpandedName(None, 'station')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 917, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
FlysEyeBeam._Automaton = _BuildAutomaton_43()




BeamFormedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfBeams'), pyxb.binding.datatypes.unsignedShort, scope=BeamFormedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 926, 5)))

BeamFormedDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'beams'), ArrayBeams, scope=BeamFormedDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 927, 5)))

def _BuildAutomaton_44 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_44
    del _BuildAutomaton_44
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 927, 5))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfBeams')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 926, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(BeamFormedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'beams')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 927, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
BeamFormedDataProduct._Automaton = _BuildAutomaton_44()




PulpSummaryDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'fileContent'), ListOfString, scope=PulpSummaryDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 953, 5)))

PulpSummaryDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'dataType'), PulsarPipelineDataType, scope=PulpSummaryDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 954, 5)))

def _BuildAutomaton_45 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_45
    del _BuildAutomaton_45
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileContent')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 953, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PulpSummaryDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 954, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    st_9._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PulpSummaryDataProduct._Automaton = _BuildAutomaton_45()




PulpDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'fileContent'), ListOfString, scope=PulpDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 963, 5)))

PulpDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'dataType'), PulsarPipelineDataType, scope=PulpDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 964, 5)))

PulpDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'arrayBeam'), ArrayBeam, scope=PulpDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 965, 5)))

def _BuildAutomaton_46 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_46
    del _BuildAutomaton_46
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileContent')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 963, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 964, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PulpDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'arrayBeam')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 965, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PulpDataProduct._Automaton = _BuildAutomaton_46()




def _BuildAutomaton_47 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_47
    del _BuildAutomaton_47
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GenericDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
GenericDataProduct._Automaton = _BuildAutomaton_47()




def _BuildAutomaton_48 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_48
    del _BuildAutomaton_48
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(UnspecifiedDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    st_7._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
UnspecifiedDataProduct._Automaton = _BuildAutomaton_48()




LinearAxis._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'increment'), pyxb.binding.datatypes.double, scope=LinearAxis, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1006, 5)))

LinearAxis._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'referencePixel'), pyxb.binding.datatypes.double, scope=LinearAxis, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1007, 5)))

LinearAxis._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'referenceValue'), pyxb.binding.datatypes.double, scope=LinearAxis, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1008, 5)))

def _BuildAutomaton_49 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_49
    del _BuildAutomaton_49
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LinearAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'number')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 996, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LinearAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'name')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 997, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LinearAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'units')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 998, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LinearAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'length')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 999, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LinearAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'increment')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1006, 5))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LinearAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'referencePixel')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1007, 5))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(LinearAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'referenceValue')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1008, 5))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    st_6._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
LinearAxis._Automaton = _BuildAutomaton_49()




def _BuildAutomaton_50 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_50
    del _BuildAutomaton_50
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TabularAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'number')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 996, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TabularAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'name')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 997, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TabularAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'units')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 998, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TabularAxis._UseForTag(pyxb.namespace.ExpandedName(None, 'length')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 999, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TabularAxis._Automaton = _BuildAutomaton_50()




DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'directionLinearAxis'), LinearAxis, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1052, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'PC0_0'), pyxb.binding.datatypes.double, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1053, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'PC0_1'), pyxb.binding.datatypes.double, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1054, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'PC1_0'), pyxb.binding.datatypes.double, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1055, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'PC1_1'), pyxb.binding.datatypes.double, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1056, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'equinox'), pyxb.binding.datatypes.string, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1057, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'raDecSystem'), RaDecSystem, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1058, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'projection'), pyxb.binding.datatypes.string, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1059, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'projectionParameters'), ListOfDouble, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1060, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'longitudePole'), Angle, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1061, 5)))

DirectionCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'latitudePole'), Angle, scope=DirectionCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1062, 5)))

def _BuildAutomaton_51 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_51
    del _BuildAutomaton_51
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=2, max=2, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1052, 5))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'directionLinearAxis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1052, 5))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'PC0_0')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1053, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'PC0_1')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1054, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'PC1_0')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1055, 5))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'PC1_1')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1056, 5))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'equinox')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1057, 5))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'raDecSystem')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1058, 5))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'projection')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1059, 5))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'projectionParameters')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1060, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'longitudePole')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1061, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DirectionCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'latitudePole')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1062, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
DirectionCoordinate._Automaton = _BuildAutomaton_51()




SpectralCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'spectralLinearAxis'), LinearAxis, scope=SpectralCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1092, 6)))

SpectralCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'spectralTabularAxis'), TabularAxis, scope=SpectralCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1093, 6)))

SpectralCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'spectralQuantity'), SpectralQuantity, scope=SpectralCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1095, 5)))

def _BuildAutomaton_52 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_52
    del _BuildAutomaton_52
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SpectralCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'spectralLinearAxis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1092, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SpectralCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'spectralTabularAxis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1093, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SpectralCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'spectralQuantity')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1095, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SpectralCoordinate._Automaton = _BuildAutomaton_52()




TimeCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeLinearAxis'), LinearAxis, scope=TimeCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1105, 6)))

TimeCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeTabularAxis'), TabularAxis, scope=TimeCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1106, 6)))

TimeCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'equinox'), EquinoxType, scope=TimeCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1108, 5)))

def _BuildAutomaton_53 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_53
    del _BuildAutomaton_53
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TimeCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'timeLinearAxis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1105, 6))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(TimeCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'timeTabularAxis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1106, 6))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(TimeCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'equinox')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1108, 5))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
TimeCoordinate._Automaton = _BuildAutomaton_53()




PolarizationCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'polarizationTabularAxis'), TabularAxis, scope=PolarizationCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1117, 5)))

PolarizationCoordinate._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'polarization'), PolarizationType, scope=PolarizationCoordinate, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1118, 5)))

def _BuildAutomaton_54 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_54
    del _BuildAutomaton_54
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=4, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1118, 5))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PolarizationCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'polarizationTabularAxis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1117, 5))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(PolarizationCoordinate._UseForTag(pyxb.namespace.ExpandedName(None, 'polarization')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1118, 5))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PolarizationCoordinate._Automaton = _BuildAutomaton_54()




PixelMapDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfAxes'), pyxb.binding.datatypes.unsignedShort, scope=PixelMapDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1132, 5)))

PixelMapDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCoordinates'), pyxb.binding.datatypes.unsignedShort, scope=PixelMapDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1133, 5)))

PixelMapDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'coordinate'), Coordinate, scope=PixelMapDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1134, 5)))

def _BuildAutomaton_55 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_55
    del _BuildAutomaton_55
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=1, max=999, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1134, 5))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfAxes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1132, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCoordinates')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1133, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(PixelMapDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'coordinate')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1134, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PixelMapDataProduct._Automaton = _BuildAutomaton_55()




ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep'), pyxb.binding.datatypes.unsignedShort, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 603, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep'), pyxb.binding.datatypes.unsignedShort, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 604, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skyModelDatabase'), pyxb.binding.datatypes.string, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 605, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'demixing'), pyxb.binding.datatypes.boolean, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 606, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'imagerIntegrationTime'), Time, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 607, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfMajorCycles'), pyxb.binding.datatypes.unsignedShort, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 608, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfInstrumentModels'), pyxb.binding.datatypes.unsignedShort, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 609, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), pyxb.binding.datatypes.unsignedShort, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 610, 5)))

ImagingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfSkyImages'), pyxb.binding.datatypes.unsignedShort, scope=ImagingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 611, 5)))

def _BuildAutomaton_56 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_56
    del _BuildAutomaton_56
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 603, 5))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 604, 5))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 605, 5))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 606, 5))
    counters.add(cc_4)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 603, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 604, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skyModelDatabase')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 605, 5))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'demixing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 606, 5))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'imagerIntegrationTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 607, 5))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfMajorCycles')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 608, 5))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfInstrumentModels')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 609, 5))
    st_17 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 610, 5))
    st_18 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_18)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ImagingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfSkyImages')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 611, 5))
    st_19 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_19)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
         ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_17, [
         ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_18, [
         ]))
    st_17._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_19, [
         ]))
    st_18._set_transitionSet(transitions)
    transitions = []
    st_19._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
ImagingPipeline._Automaton = _BuildAutomaton_56()




CalibrationPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep'), pyxb.binding.datatypes.unsignedShort, scope=CalibrationPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 620, 5)))

CalibrationPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep'), pyxb.binding.datatypes.unsignedShort, scope=CalibrationPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 621, 5)))

CalibrationPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'flagAutoCorrelations'), pyxb.binding.datatypes.boolean, scope=CalibrationPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 622, 5)))

CalibrationPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'demixing'), pyxb.binding.datatypes.boolean, scope=CalibrationPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 623, 5)))

CalibrationPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skyModelDatabase'), pyxb.binding.datatypes.string, scope=CalibrationPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 624, 5)))

CalibrationPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfInstrumentModels'), pyxb.binding.datatypes.unsignedShort, scope=CalibrationPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 625, 5)))

CalibrationPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), pyxb.binding.datatypes.unsignedShort, scope=CalibrationPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 626, 5)))

def _BuildAutomaton_57 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_57
    del _BuildAutomaton_57
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 620, 5))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 621, 5))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 622, 5))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 623, 5))
    counters.add(cc_4)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 620, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 621, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'flagAutoCorrelations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 622, 5))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'demixing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 623, 5))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skyModelDatabase')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 624, 5))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfInstrumentModels')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 625, 5))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CalibrationPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 626, 5))
    st_17 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    transitions.append(fac.Transition(st_12, [
         ]))
    transitions.append(fac.Transition(st_13, [
         ]))
    transitions.append(fac.Transition(st_14, [
         ]))
    transitions.append(fac.Transition(st_15, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_15, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
         ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_17, [
         ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    st_17._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CalibrationPipeline._Automaton = _BuildAutomaton_57()




AveragingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep'), pyxb.binding.datatypes.unsignedShort, scope=AveragingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 635, 5)))

AveragingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep'), pyxb.binding.datatypes.unsignedShort, scope=AveragingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 636, 5)))

AveragingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'flagAutoCorrelations'), pyxb.binding.datatypes.boolean, scope=AveragingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 637, 5)))

AveragingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'demixing'), pyxb.binding.datatypes.boolean, scope=AveragingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 638, 5)))

AveragingPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts'), pyxb.binding.datatypes.unsignedShort, scope=AveragingPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 639, 5)))

def _BuildAutomaton_58 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_58
    del _BuildAutomaton_58
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'frequencyIntegrationStep')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 635, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'timeIntegrationStep')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 636, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'flagAutoCorrelations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 637, 5))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'demixing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 638, 5))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AveragingPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCorrelatedDataProducts')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 639, 5))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
         ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
         ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
         ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    st_15._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
AveragingPipeline._Automaton = _BuildAutomaton_58()




PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'pulsarSelection'), PulsarSelectionType, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 663, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'pulsars'), ListOfString, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 664, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'doSinglePulseAnalysis'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 665, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'convertRawTo8bit'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 666, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subintegrationLength'), Time, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 667, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skipRFIExcision'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 668, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skipDataFolding'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 669, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skipOptimizePulsarProfile'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 670, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skipConvertRawIntoFoldedPSRFITS'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 671, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'runRotationalRAdioTransientsAnalysis'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 672, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skipDynamicSpectrum'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 673, 5)))

PulsarPipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'skipPreFold'), pyxb.binding.datatypes.boolean, scope=PulsarPipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 674, 5)))

def _BuildAutomaton_59 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_59
    del _BuildAutomaton_59
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pulsarSelection')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 663, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pulsars')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 664, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'doSinglePulseAnalysis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 665, 5))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'convertRawTo8bit')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 666, 5))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'subintegrationLength')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 667, 5))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skipRFIExcision')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 668, 5))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skipDataFolding')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 669, 5))
    st_17 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skipOptimizePulsarProfile')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 670, 5))
    st_18 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_18)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skipConvertRawIntoFoldedPSRFITS')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 671, 5))
    st_19 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_19)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'runRotationalRAdioTransientsAnalysis')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 672, 5))
    st_20 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_20)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skipDynamicSpectrum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 673, 5))
    st_21 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_21)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(PulsarPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'skipPreFold')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 674, 5))
    st_22 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_22)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
         ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
         ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
         ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
         ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_17, [
         ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_18, [
         ]))
    st_17._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_19, [
         ]))
    st_18._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_20, [
         ]))
    st_19._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_21, [
         ]))
    st_20._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_22, [
         ]))
    st_21._set_transitionSet(transitions)
    transitions = []
    st_22._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
PulsarPipeline._Automaton = _BuildAutomaton_59()




def _BuildAutomaton_60 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_60
    del _BuildAutomaton_60
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CosmicRayPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CosmicRayPipeline._Automaton = _BuildAutomaton_60()




LongBaselinePipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subbandsPerSubbandGroup'), pyxb.binding.datatypes.unsignedShort, scope=LongBaselinePipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 688, 5)))

LongBaselinePipeline._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'subbandGroupsPerMS'), pyxb.binding.datatypes.unsignedShort, scope=LongBaselinePipeline, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 689, 5)))

def _BuildAutomaton_61 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_61
    del _BuildAutomaton_61
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'subbandsPerSubbandGroup')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 688, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(LongBaselinePipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'subbandGroupsPerMS')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 689, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    st_12._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
LongBaselinePipeline._Automaton = _BuildAutomaton_61()




def _BuildAutomaton_62 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_62
    del _BuildAutomaton_62
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 258, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'observationId')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 259, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'parset')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 260, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 261, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'strategyDescription')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 262, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'startTime')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 263, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'duration')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 264, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'relations')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 265, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 589, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'pipelineVersion')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 590, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(GenericPipeline._UseForTag(pyxb.namespace.ExpandedName(None, 'sourceData')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 591, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    st_10._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
GenericPipeline._Automaton = _BuildAutomaton_62()




SkyImageDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'locationFrame'), LocationFrame, scope=SkyImageDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1151, 5)))

SkyImageDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'timeFrame'), pyxb.binding.datatypes.string, scope=SkyImageDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1152, 5)))

SkyImageDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'observationPointing'), Pointing, scope=SkyImageDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1153, 5)))

SkyImageDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'restoringBeamMajor'), Angle, scope=SkyImageDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1154, 5)))

SkyImageDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'restoringBeamMinor'), Angle, scope=SkyImageDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1155, 5)))

SkyImageDataProduct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'rmsNoise'), Pixel, scope=SkyImageDataProduct, location=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1156, 5)))

def _BuildAutomaton_63 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_63
    del _BuildAutomaton_63
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=1, max=999, metadata=pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1134, 5))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductType')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 790, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'dataProductIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 791, 3))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'storageTicket')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 792, 3))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'size')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 793, 3))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'checksum')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 794, 3))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileName')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 795, 3))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'fileFormat')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 796, 3))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'processIdentifier')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 797, 3))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfAxes')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1132, 5))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'numberOfCoordinates')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1133, 5))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'coordinate')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1134, 5))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'locationFrame')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1151, 5))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'timeFrame')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1152, 5))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'observationPointing')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1153, 5))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'restoringBeamMajor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1154, 5))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'restoringBeamMinor')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1155, 5))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(SkyImageDataProduct._UseForTag(pyxb.namespace.ExpandedName(None, 'rmsNoise')), pyxb.utils.utility.Location('/home/jkuensem/dev/SIP-lib/SIPlib-Task9091/LTA/sip/lib/LTA-SIP.xsd', 1156, 5))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    transitions.append(fac.Transition(st_5, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_11, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
         ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
         ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
         ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
         ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    st_16._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
SkyImageDataProduct._Automaton = _BuildAutomaton_63()

