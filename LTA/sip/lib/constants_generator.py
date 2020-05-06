#!/usr/bin/env python3

# This module can be used to auto-generate a list of constant definitions based on value restrictions (defined as
# enumerations in the XSD). These are dynamically retrieved from the pyxb-generated API module and in most cases can
# just be rerun after pyxb to update the constants module after something has changed in the XSD schema definition.

from . import ltasip
import inspect
import pyxb
#from collections import namedtuple

VERSION = "SIPlib Constants Generator 0.1"

ltasip.Namespace.setPrefix('sip')

def __safeupper(name):
    name = name.replace (" ", "_")
    name = name.replace ("+", "_")
    name = name.replace ("/", "_")
    name = name.replace ("-", "_")
    name = name.replace ("(", "_")
    name = name.replace (")", "_")
    name = name.replace (",", "_")
    name = name.replace (".", "_")
    name = name.replace ("'", "_")
    name = name.upper()
    return name



def get_constants_for_resctrictedtypes():

    enumtypes=[]
    for name, obj in inspect.getmembers(ltasip):
        if inspect.isclass(obj) and issubclass(obj,pyxb.binding.basis.enumeration_mixin) and not "STD_ANON" in str(obj):
            enumtypes.append(obj)
               # Excluded here:
               # ltasip.STD_ANON_  # clock frequencies, see below
               # ltasip.STD_ANON   # coordinateSystem, see below


    __constants = dict()
    for type in enumtypes:
        for value in list(type.values()):
            name = str(type.__name__).upper()+"_"+__safeupper(str(value))
            __constants[name] = value

    # These anonymous ones need a proper name:
    for value in list(ltasip.STD_ANON_.values()):
        __constants["FREQUENCY_"+__safeupper(str(value))]=value
    for value in list(ltasip.STD_ANON.values()):
        __constants["COORDINATESYSTEM_"+__safeupper(str(value))]=value

    # to convert to named tuple for object-like access (dot-notation):
    # constants = namedtuple('Constants', __constants)._make(__constants[key] for key in __constants.keys())
    # e.g. allows: print constants.OBSERVINGMODETYPE_DIRECT_DATA_STORAGE
    # (It does not allow discovery by IDEs and such, but may be useful some time, maybe in interactive shells.)

    return __constants


def main(path):

    constants =  get_constants_for_resctrictedtypes()

    with open(path, 'w+') as f:
        f.write("# This module creates constants for conveniently meeting permitted values when composing SIP files "
                "in SIPlib. "
                "\n# Auto-generated based on Pyxb API by "+VERSION+"\n\n")
        for key in sorted(constants.keys()):
            #type = type(constants.get(key))
            value = constants.get(key)
            if isinstance(value, str):
                value = "\""+value+"\""
            else:
                value = str(value)
            line = key+"="+value+"\n"
            print(line, end=' ')
            f.write(line)


if __name__ == '__main__':
    path="constants.py"
    main(path)

