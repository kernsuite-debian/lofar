#!/usr/bin/env python3

# This module provides functions for easy creation of a Lofar LTA SIP document.
# It builds upon a Pyxb-generated API from the schema definition, which is very clever but hard to use, since
# the arguments in class constructors and functions definitions are not verbose and there is no intuitive way
# to determine the mandatory and optional elements to create a valid SIP document. This module is designed to
# provide easy-to-use functions that bridges this shortcoming of the Pyxb API.
#
# Usage: Import module. Create an instance of Sip.
#        Add elements through the Sip.add_X functions. Many require instances of other classes of the module.
#        call getprettyxml() and e.g. save to disk.
#
# Note on validation: From construction through every addition, the SIP should remain valid (or throw an error
# that clearly points out where e.g. a given value does not meet the restrictions of the SIP schema.
#
# Note on code structure: This has to be seen as a compromise between elegant and maintainable code with well-
# structured inheritance close to the schema definition on the one hand, and something more straightforward to use,
# with flatter hierarchies on the other hand.
#
# Note on parameter maps:  The ...Map objects are helper objects to create dictionaries for the commonly used
# constructor arguments of several other objects. This could alternatively also be implemented via inheritance from
# a supertype, and indeed is solved like this in the pyxb code. However, this then requires the use of an argument
# list pointer, which hides the list of required and optional arguments from the user. Alternatively, all arguments
# have to be mapped in all constructors repeatedly, creating lots of boilerplate code. This is the nicest approach
# I could think of that keeps the whole thing reasonably maintainable AND usable.


from . import ltasip
import pyxb
from . import constants
import os
import uuid
import xml.dom.minidom
from pyxb.namespace import XMLSchema_instance as xsi
from pyxb.namespace import XMLNamespaces as xmlns
from . import query


VERSION = "SIPlib 0.4"
d = os.path.dirname(os.path.realpath(__file__))
STATION_CONFIG_PATH = d+'/station_coordinates.conf'
ltasip.Namespace.setPrefix('sip')

# todo: create docstrings for everything.
# specify types and explain purpose of the field (-> ask someone with more astronomical background)

# todo: check what fields can be implicitely set
# (e.g. parameter type in dataproduct may be derived from the specific dataproduct class that is used)
# Some parameters may also be filled with a reasonable default value. Right now, usually only optional values
# as per schema definition are optional parameters.


def print_user_warning():
    print("!!! You are accessing an object, which is based on code that was auto-generated with the pyxb package.")
    print("!!! We strongly advise you to only use the datatypes of the siplib wrapper to create your SIP file.")
    print("!!! If you choose to alter pyxb/ltasip objects or their values directly for some reason, your SIP may ")
    print("!!! become invalid. - Please make sure to validate your SIP before submission! ")
    print("!!! Note that the pyxb portion of the code is subject to change whitout being backwards compatible.")
    print("!!! This means that, should you choose to access pyxb objects e.g. to parse an existing SIP file, things")
    print("!!! might break for you without further warning.")
    print("!!! (You may suppress this warning by setting the flag in the pyxb-related getter/setter functions.)")

# ===============================
# Identifier definition (used for LTA entities, i-e- processes and dataproducts):

class Identifier(object):
    """ Identifier for LTA entities. """
    def __init__(self,
                 source,
                 userlabel=None,
    ):
        """
        The default Identifier constructor creates a new unique identifier in the LTA catalog.
        An optional userlabel can be assigned to later query the identifier based on this String.
        Throws an exception if the given label already exists for the given source.
        """
        unique_id = query.create_unique_id(source, userlabel)
        self.__pyxb_identifier=ltasip.IdentifierType(
            source=str(source),
            identifier=str(unique_id),
            name = "",
            label=userlabel)

    @classmethod
    def lookup(cls,
               source,
               userlabel):
        """
        Queries an existing LTA identifier from the catalog based on it's userlabel (which had to be assigned
        at the time the Identifier is created to allow this lookup to work).
        Throws an exception if the given label does not exist for the given source.
        """
        unique_id = query.get_unique_id(source, userlabel)
        identifier = Identifier.__new__(Identifier)
        identifier._set_pyxb_identifier(
            ltasip.IdentifierType(
                source=str(source),
                identifier=str(unique_id),
                name = "",
                label=userlabel),
            suppress_warning=True)
        return identifier

    def _set_pyxb_identifier(self, pyxb_identifier, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        self.__pyxb_identifier = pyxb_identifier

    def _get_pyxb_identifier(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_identifier

# ===============================
# Station definitions:

class Station():
    def __init__(self,
                 name,
                 type,
                 antennafield1,
                 antennafield2=None
                ):

        __afields=[antennafield1._get_pyxb_antennafield(suppress_warning=True)]
        if antennafield2:
            __afields.append(antennafield2._get_pyxb_antennafield(suppress_warning=True))
        self.__pyxb_station=ltasip.Station(
            name=name,
            stationType=type,
            antennaField=__afields
            )

    @classmethod
    def preconfigured(cls,
                      name,
                      antennafieldtypes
    ):
        if antennafieldtypes is None or len(antennafieldtypes)>2:
            raise Exception("please specify a list with one or two antennafield types for station:",name)

        __afield1=None
        __afield2=None
        with open(STATION_CONFIG_PATH, 'r') as f:
            for line in f.readlines():
                if line.strip():
                  field_coords = eval("dict("+line+")")  # literal_eval does not accept dict definition via constructor. Make sure config file is not writable to prevent code execution!
                  for type in antennafieldtypes:
                    if field_coords["name"] == name+"_"+type:
                        __afield=AntennafieldXYZ(
                            type=type,
                            coordinate_system=field_coords["coordinate_system"],
                            coordinate_unit=constants.LENGTHUNIT_M, # Does this make sense? I have to give a lenght unit accoridng to the XSD, but ICRF should be decimal degrees?!
                            coordinate_x=field_coords["x"],
                            coordinate_y=field_coords["y"],
                            coordinate_z=field_coords["z"])
                        if not __afield1:
                            __afield1=__afield
                        elif not __afield2:
                            __afield2=__afield

        if not __afield1:
            raise Exception("no matching coordinates found for station:", name,"and fields",str(antennafieldtypes))

        if name.startswith( 'CS' ):
            sttype = "Core"
        elif name.startswith( "RS" ):
            sttype = "Remote"
        else:
            sttype = "International"

        return cls(
                name=name,
                type=sttype,
                antennafield1=__afield1,
                antennafield2=__afield2,
                )

    def _get_pyxb_station(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_station



class AntennafieldXYZ():
    def __init__(self,
                 type,
                 coordinate_system,
                 coordinate_x,
                 coordinate_y,
                 coordinate_z,
                 coordinate_unit):
        self.__pyxb_antennafield=ltasip.AntennaField(
            name=type,
            location=ltasip.Coordinates(
                coordinateSystem=coordinate_system,
                x=ltasip.Length(coordinate_x, units=coordinate_unit),
                y=ltasip.Length(coordinate_y, units=coordinate_unit),
                z=ltasip.Length(coordinate_z, units=coordinate_unit)
            )
        )

    def _get_pyxb_antennafield(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_antennafield

class AntennafieldRadLonLat():
    def __init__(self,
                 type,
                 coordinate_system,
                 coordinate_radius,
                 coordinate_radiusunit,
                 coordinate_longitude,
                 coordinate_latitude,
                 coordinate_lonlatunit,
                 ):
        self.__pyxb_antennafield=ltasip.AntennaField(
            name=type,
            location=ltasip.Coordinates(
                coordinateSystem=coordinate_system,
                radius=ltasip.Length(coordinate_radius, units=coordinate_radiusunit),
                longitude=ltasip.Angle(coordinate_longitude, units=coordinate_lonlatunit),
                latitude=ltasip.Angle(coordinate_latitude, units=coordinate_lonlatunit)
            )
        )

    def _get_pyxb_antennafield(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_antennafield


# ============
# PipelineRuns:

class PipelineMap():
    def __init__(self,
                 name,
                 version,
                 sourcedata_identifiers,
                 process_map
    ):

        __sourcedata=ltasip.DataSources()
        for identifier in sourcedata_identifiers:
            __sourcedata.append(identifier._get_pyxb_identifier(suppress_warning=True))

        self.pipeline_map=dict(
            pipelineName=name,
            pipelineVersion=version,
            sourceData=__sourcedata
        )
        self.pipeline_map.update(process_map.get_dict())

    def get_dict(self):
        return self.pipeline_map


class SimplePipeline():
    def __init__(self, pipeline_map):
        self.__pyxb_pipeline=ltasip.PipelineRun(**pipeline_map.get_dict())

    def _get_pyxb_pipeline(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pipeline


class ImagingPipeline():
    def __init__(self,
                 pipeline_map,
                 imagerintegrationtime,
                 imagerintegrationtime_unit,
                 numberofmajorcycles,
                 numberofinstrumentmodels,
                 numberofcorrelateddataproducts,
                 numberofskyimages,
                 frequencyintegrationstep=None,
                 timeintegrationstep=None,
                 skymodeldatabase=None,
                 demixing=None):

        self.__pyxb_pipeline=ltasip.ImagingPipeline(
            frequencyIntegrationStep=frequencyintegrationstep,
            timeIntegrationStep=timeintegrationstep,
            skyModelDatabase=skymodeldatabase,
            demixing=demixing,
            imagerIntegrationTime=(ltasip.Time(imagerintegrationtime, units=imagerintegrationtime_unit)),
            numberOfMajorCycles=numberofmajorcycles,
            numberOfInstrumentModels=numberofinstrumentmodels,
            numberOfCorrelatedDataProducts=numberofcorrelateddataproducts,
            numberOfSkyImages=numberofskyimages,
            **pipeline_map.get_dict()
        )

    def _get_pyxb_pipeline(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pipeline


class CalibrationPipeline():
    def __init__(self,
                 pipeline_map,
                 skymodeldatabase,
                 numberofinstrumentmodels,
                 numberofcorrelateddataproducts,
                 frequencyintegrationstep=None,
                 timeintegrationstep=None,
                 flagautocorrelations=None,
                 demixing=None):
        self.__pyxb_pipeline=ltasip.CalibrationPipeline(
            frequencyIntegrationStep=frequencyintegrationstep,
            timeIntegrationStep=timeintegrationstep,
            flagAutoCorrelations=flagautocorrelations,
            demixing=demixing,
            skyModelDatabase=skymodeldatabase,
            numberOfInstrumentModels=numberofinstrumentmodels,
            numberOfCorrelatedDataProducts=numberofcorrelateddataproducts,
            **pipeline_map.get_dict()
        )

    def _get_pyxb_pipeline(self, suppress_warning=False):
        return self.__pyxb_pipeline

class AveragingPipeline():
    def __init__(self,
                 pipeline_map,
                 numberofcorrelateddataproducts,
                 frequencyintegrationstep,
                 timeintegrationstep,
                 flagautocorrelations,
                 demixing):
        self.__pyxb_pipeline=ltasip.AveragingPipeline(
            frequencyIntegrationStep=frequencyintegrationstep,
            timeIntegrationStep=timeintegrationstep,
            flagAutoCorrelations=flagautocorrelations,
            demixing=demixing,
            numberOfCorrelatedDataProducts=numberofcorrelateddataproducts,
            **pipeline_map.get_dict()
        )
        #self.__pyxb_pipeline._setAttribute("xsi:type","ns1:AveragingPipeline")

    def _get_pyxb_pipeline(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pipeline


class PulsarPipeline():
    def __init__(self,
                 pipeline_map,
                 pulsarselection,
                 pulsars,
                 dosinglepulseanalysis,
                 convertRawTo8bit,
                 subintegrationlength,
                 subintegrationlength_unit,
                 skiprfiexcision,
                 skipdatafolding,
                 skipoptimizepulsarprofile,
                 skipconvertrawintofoldedpsrfits,
                 runrotationalradiotransientsanalysis,
                 skipdynamicspectrum,
                 skipprefold):

        self.__pyxb_pipeline=ltasip.PulsarPipeline(
            pulsarSelection=pulsarselection,
	    	pulsars=pulsars,
            doSinglePulseAnalysis=dosinglepulseanalysis,
            convertRawTo8bit=convertRawTo8bit,
            subintegrationLength=ltasip.Time(subintegrationlength , units=subintegrationlength_unit),
            skipRFIExcision=skiprfiexcision,
            skipDataFolding=skipdatafolding,
            skipOptimizePulsarProfile=skipoptimizepulsarprofile,
            skipConvertRawIntoFoldedPSRFITS=skipconvertrawintofoldedpsrfits,
            runRotationalRAdioTransientsAnalysis=runrotationalradiotransientsanalysis,
			skipDynamicSpectrum=skipdynamicspectrum,
        	skipPreFold=skipprefold,
            **pipeline_map.get_dict()
        )
    def _get_pyxb_pipeline(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pipeline

class CosmicRayPipeline():
    def __init__(self, pipeline_map):
        self.__pyxb_pipeline=ltasip.CosmicRayPipeline(**pipeline_map.get_dict())

    def _get_pyxb_pipeline(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pipeline

class LongBaselinePipeline():
    def __init__(self,
                 pipeline_map,
                 subbandspersubbandgroup,
                 subbandgroupspermS
    ):
        self.__pyxb_pipeline=ltasip.LongBaselinePipeline(
            subbandsPerSubbandGroup=subbandspersubbandgroup,
            subbandGroupsPerMS=subbandgroupspermS,
            **pipeline_map.get_dict())

    def _get_pyxb_pipeline(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pipeline

class GenericPipeline():
    def __init__(self, pipeline_map):
        self.__pyxb_pipeline=ltasip.GenericPipeline(**pipeline_map.get_dict())

    def _get_pyxb_pipeline(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pipeline




# ==========
# Dataproducts:

class DataProductMap():
    def __init__(self,
                 type,
                 identifier,
                 size,
                 filename,
                 fileformat,
                 process_identifier,
                 checksum_md5=None,
                 checksum_adler32=None,
                 storageticket=None
    ):
        self.dataproduct_map= dict(dataProductType=type,
                                   dataProductIdentifier=identifier._get_pyxb_identifier(suppress_warning=True),
                                   size=size,
                                   fileName=filename, fileFormat=fileformat,
                                   processIdentifier=process_identifier._get_pyxb_identifier(suppress_warning=True),
                                   storageTicket=storageticket)

        checksums = []
        if checksum_md5 is not None:
            checksums = checksums + [ltasip.ChecksumType(algorithm="MD5", value_=checksum_md5)]
        if checksum_adler32 is not None:
            checksums = checksums + [ltasip.ChecksumType(algorithm="Adler32", value_=checksum_adler32)]
        self.dataproduct_map["checksum"]=checksums

    def get_dict(self):
        return self.dataproduct_map


class __DataProduct(object):

    def __init__(self, pyxb_dataproduct):
        self.__pyxb_dataproduct=pyxb_dataproduct

    def set_identifier(self, identifier):
        self.__pyxb_dataproduct.dataProductIdentifier = identifier._get_pyxb_identifier(suppress_warning=True)

    def set_process_identifier(self, identifier):
        self.__pyxb_dataproduct.processIdentifier = identifier._get_pyxb_identifier(suppress_warning=True)

    def _get_pyxb_dataproduct(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_dataproduct


class SimpleDataProduct(__DataProduct):
    def __init__(self, dataproduct_map):
        super(SimpleDataProduct, self).__init__(
            ltasip.DataProduct(**dataproduct_map.get_dict())
        )

class SkyModelDataProduct(__DataProduct):
    def __init__(self, dataproduct_map):
        super(SkyModelDataProduct, self).__init__(
            ltasip.SkyModelDataProduct(**dataproduct_map.get_dict())
        )

class GenericDataProduct(__DataProduct):
    def __init__(self, dataproduct_map):
        super(GenericDataProduct, self).__init__(
            ltasip.GenericDataProduct(**dataproduct_map.get_dict())
        )


class UnspecifiedDataProduct(__DataProduct):
    def __init__(self, dataproduct_map):
        super(UnspecifiedDataProduct, self).__init__(
            ltasip.UnspecifiedDataProduct(**dataproduct_map.get_dict())
        )


class PixelMapDataProduct(__DataProduct):
    def __init__(self,
                 dataproduct_map,
                 numberofaxes,
                 coordinates):
        super(PixelMapDataProduct, self).__init__(
          ltasip.PixelMapDataProduct(
            numberOfAxes=numberofaxes,
            numberOfCoordinates=len(coordinates),
            coordinate = [x._get_pyxb_coordinate(suppress_warning=True) for x in coordinates],
            **dataproduct_map.get_dict())
        )


class SkyImageDataProduct(__DataProduct):
    def __init__(self,
                 dataproduct_map,
                 numberofaxes,
                 coordinates,
                 locationframe,
                 timeframe,
                 observationpointing,
                 restoringbeammajor_angle,
                 restoringbeammajor_angleunit,
                 restoringbeamminor_angle,
                 restoringbeamminor_angleunit,
                 rmsnoise):


          super(SkyImageDataProduct, self).__init__(
            ltasip.SkyImageDataProduct(
              numberOfAxes=numberofaxes,
              numberOfCoordinates=len(coordinates),
              coordinate = [x._get_pyxb_coordinate(suppress_warning=True) for x in coordinates],
              locationFrame=locationframe,
              timeFrame=timeframe,
              observationPointing=observationpointing._get_pyxb_pointing(suppress_warning=True),
              restoringBeamMajor=ltasip.Angle(restoringbeammajor_angle, units=restoringbeammajor_angleunit),
              restoringBeamMinor=ltasip.Angle(restoringbeamminor_angle, units=restoringbeamminor_angleunit),
              rmsNoise=ltasip.Pixel(rmsnoise, units="Jy/beam"),
              **dataproduct_map.get_dict())
          )



class CorrelatedDataProduct(__DataProduct):
    def __init__(self,
                 dataproduct_map,
                 subarraypointing_identifier,
                 subband,
                 starttime,
                 duration,
                 integrationinterval,
                 integrationintervalunit,
                 central_frequency,
                 central_frequencyunit,
                 channelwidth_frequency,
                 channelwidth_frequencyunit,
                 channelspersubband,
                 stationsubband=None):
        super(CorrelatedDataProduct, self).__init__(
          ltasip.CorrelatedDataProduct(
            subArrayPointingIdentifier=subarraypointing_identifier._get_pyxb_identifier(suppress_warning=True),
            centralFrequency=ltasip.Frequency(central_frequency, units=central_frequencyunit),
            channelWidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit),
            subband=subband,
            startTime=starttime,
            duration=duration,
            integrationInterval=ltasip.Time(integrationinterval,units=integrationintervalunit),
            channelsPerSubband=channelspersubband,
            stationSubband=stationsubband,
            **dataproduct_map.get_dict()
          )
        )

    def set_subarraypointing_identifier(self, identifier):
        self.__pyxb_dataproduct.subArrayPointingIdentifier = identifier._get_pyxb_identifier(suppress_warning=True)



class InstrumentModelDataProduct(__DataProduct):
    def __init__(self, dataproduct_map):
        super(InstrumentModelDataProduct, self).__init__(
            ltasip.InstrumentModelDataProduct(**dataproduct_map.get_dict())
        )


class TransientBufferBoardDataProduct(__DataProduct):
    def __init__(self,
                 dataproduct_map,
                 numberofsamples,
                 timestamp,
                 triggertype,
                 triggervalue):
        super(TransientBufferBoardDataProduct, self).__init__(
          ltasip.TransientBufferBoardDataProduct(
            numberOfSamples=numberofsamples,
            timeStamp=timestamp,
            triggerParameters=ltasip.TBBTrigger(type=triggertype,value=triggervalue),
            **dataproduct_map.get_dict())
        )


class PulpSummaryDataProduct(__DataProduct):
    def __init__(self,
                 dataproduct_map,
                 filecontent,
                 datatype):

        super(PulpSummaryDataProduct, self).__init__(
          ltasip.PulpSummaryDataProduct(
            fileContent=filecontent,
            dataType=datatype,
            **dataproduct_map.get_dict())
        )


class PulpDataProduct(__DataProduct):
    def __init__(self,
                 dataproduct_map,
                 filecontent,
                 datatype,
                 arraybeam):

        super(PulpDataProduct, self).__init__(
          ltasip.PulpDataProduct(
            fileContent=filecontent,
            dataType=datatype,
            arrayBeam=arraybeam._get_pyxb_beam(suppress_warning=True),
            **dataproduct_map.get_dict())
        )


class BeamFormedDataProduct(__DataProduct):
    def __init__(self,
                 dataproduct_map,
                 #numberofbeams,
                 beams=None):

        __beams=None
        __nbeams=0
        if beams:
            __beams=ltasip.ArrayBeams()
            __nbeams = len(beams)
            for beam in beams:
                __beams.append(beam._get_pyxb_beam(suppress_warning=True))
        super(BeamFormedDataProduct, self).__init__(
          ltasip.BeamFormedDataProduct(
            numberOfBeams=__nbeams,
            beams=__beams,
            **dataproduct_map.get_dict())
        )




# ============
# Coordinates:

class SpectralCoordinate():
    def __init__(self,
                 quantity_type,
                 quantity_value,
                 axis,
                 ):

        args = dict(spectralQuantity=ltasip.SpectralQuantity(value_=quantity_value, type=quantity_type))

        if isinstance(axis, LinearAxis):
            args.update(dict(spectralLinearAxis=axis._get_pyxb_axis(suppress_warning=True)))
        elif isinstance(axis, TabularAxis):
            args.update(dict(spectralTabularAxis=axis._get_pyxb_axis(suppress_warning=True)))
        else:
            print("wrong axis type:",type(axis))

        self.__pyxb_coordinate=ltasip.SpectralCoordinate(**args)

    def _get_pyxb_coordinate(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_coordinate


class TimeCoordinate():
    def __init__(self,
                 equinox,
                 axis,
                 ):

        args = dict(equinox=equinox)

        if isinstance(axis, LinearAxis):
            args.update(dict(timeLinearAxis=axis._get_pyxb_axis(suppress_warning=True)))
        elif isinstance(axis, TabularAxis):
            args.update(dict(timeTabularAxis=axis._get_pyxb_axis(suppress_warning=True)))
        else:
            print("wrong axis type:",type(axis))

        self.__pyxb_coordinate=ltasip.TimeCoordinate(**args)


    def _get_pyxb_coordinate(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_coordinate


class PolarizationCoordinate():
    def __init__(self,
                 tabularaxis,
                 polarizations
    ):
        self.__pyxb_coordinate=ltasip.PolarizationCoordinate(
            polarizationTabularAxis=tabularaxis._get_pyxb_axis(suppress_warning=True),
            polarization=polarizations)

    def _get_pyxb_coordinate(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_coordinate


class DirectionCoordinate():
    def __init__(self,
                 linearaxis_a,
                 linearaxis_b,
                 pc0_0,
                 pc0_1,
                 pc1_0,
                 pc1_1,
                 equinox,
                 radecsystem,
                 projection,
                 projectionparameters,
                 longitudepole_angle,
                 longitudepole_angleunit,
                 latitudepole_angle,
                 latitudepole_angleunit):

        self.__pyxb_coordinate=ltasip.DirectionCoordinate(
            directionLinearAxis=[linearaxis_a._get_pyxb_axis(suppress_warning=True), linearaxis_b._get_pyxb_axis(suppress_warning=True)],
            PC0_0=pc0_0,
            PC0_1=pc0_1,
            PC1_0=pc1_0,
            PC1_1=pc1_1,
            equinox=equinox,
            raDecSystem=radecsystem,
            projection=projection,
            projectionParameters=projectionparameters,
            longitudePole=ltasip.Angle(longitudepole_angle, units=longitudepole_angleunit),
            latitudePole=ltasip.Angle(latitudepole_angle, units=latitudepole_angleunit)
        )

    def _get_pyxb_coordinate(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_coordinate

# ###########
# ArrayBeams:

class ArrayBeamMap():
    def __init__(self,
                 subarraypointing_identifier,
                 beamnumber,
                 dispersionmeasure,
                 numberofsubbands,
                 stationsubbands,
                 samplingtime,
                 samplingtimeunit,
                 centralfrequencies,
                 centralfrequencies_unit,
                 channelwidth_frequency,
                 channelwidth_frequencyunit,
                 channelspersubband,
                 stokes):
        self.arraybeam_map=dict(
            subArrayPointingIdentifier=subarraypointing_identifier._get_pyxb_identifier(suppress_warning=True),
            beamNumber=beamnumber,
            dispersionMeasure=dispersionmeasure,
            numberOfSubbands=numberofsubbands,
            stationSubbands=stationsubbands,
            samplingTime=ltasip.Time(samplingtime, units=samplingtimeunit),
            centralFrequencies=ltasip.ListOfFrequencies(frequencies=centralfrequencies, unit=centralfrequencies_unit),
            channelWidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit),
            channelsPerSubband=channelspersubband,
            stokes=stokes
        )

    def get_dict(self):
        return self.arraybeam_map

class SimpleArrayBeam():
    def __init__(self, arraybeam_map):
        self.__pyxb_beam=ltasip.ArrayBeam(**arraybeam_map.get_dict())

    def _get_pyxb_beam(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_beam


class CoherentStokesBeam():
    def __init__(self,
                 arraybeam_map,
                 pointing,
                 offset):
        self.__pyxb_beam=ltasip.CoherentStokesBeam(
            pointing=pointing,
            offset=offset,
            **arraybeam_map.get_dict())

    def _get_pyxb_beam(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_beam


class IncoherentStokesBeam():
    def __init__(self, arraybeam_map):
        self.__pyxb_beam=ltasip.IncoherentStokesBeam(**arraybeam_map.get_dict())

    def _get_pyxb_beam(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_beam


class FlysEyeBeam():
    def __init__(self,
                 arraybeam_map,
                 station):
        self.__pyxb_beam=ltasip.FlysEyeBeam(
            station=station._get_pyxb_station(suppress_warning=True),
            **arraybeam_map.get_dict())

    def _get_pyxb_beam(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_beam


# ###################
# Online processings:

class CorrelatorProcessing():
    def __init__(self,
                 integrationinterval,
                 integrationinterval_unit,
                 channelwidth_frequency=None,
                 channelwidth_frequencyunit=None,
                 channelspersubband=None,
                 processingtype="Correlator",
                 ):

        __channelwidth=None
        if channelwidth_frequency and channelwidth_frequencyunit:
            __channelwidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit),

        self.__pyxb_rtprocessing=ltasip.Correlator(
            integrationInterval=ltasip.Time(integrationinterval,units=integrationinterval_unit),
            processingType=processingtype,
        #    channelWidth=__channelwidth,
            channelsPerSubband=channelspersubband
        )

        # Somehow this does not work in the constructor:
        self.__pyxb_rtprocessing.channelwidth=__channelwidth

    def _get_pyxb_rtprocessing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_rtprocessing

class CoherentStokesProcessing():
    def __init__(self,
                 rawsamplingtime,
                 rawsamplingtime_unit,
                 timesamplingdownfactor,
                 samplingtime,
                 samplingtime_unit,
                 stokes,
                 numberofstations,
                 stations,
                 frequencydownsamplingfactor=None,
                 numberofcollapsedchannels=None,
                 channelwidth_frequency=None,
                 channelwidth_frequencyunit=None,
                 channelspersubband=None,
                 processingtype="Coherent Stokes",
                 ):

        __stations = ltasip.Stations()
        for station in stations:
            __stations.append(station._get_pyxb_station(suppress_warning=True))

        __channelwidth=None
        if channelwidth_frequency and channelwidth_frequencyunit:
            __channelwidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit)

        self.__pyxb_rtprocessing=ltasip.CoherentStokes(
            rawSamplingTime=ltasip.Time(rawsamplingtime, units=rawsamplingtime_unit),
			timeDownsamplingFactor=timesamplingdownfactor,
			samplingTime=ltasip.Time(samplingtime, units=samplingtime_unit),
            frequencyDownsamplingFactor=frequencydownsamplingfactor,
			numberOfCollapsedChannels=numberofcollapsedchannels,
            stokes=stokes,
		    numberOfStations=numberofstations,
            stations=__stations,
            #channelWidth=__channelwidth,
            channelsPerSubband=channelspersubband,
            processingType=processingtype
            )

        # Somehow this does not work in the constructor:
        self.__pyxb_rtprocessing.channelwidth=__channelwidth

    def _get_pyxb_rtprocessing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_rtprocessing

# This is identical to coherent stokes. Redundancy already in the SIP schema...
class IncoherentStokesProcessing():
    def __init__(self,
                 rawsamplingtime,
                 rawsamplingtime_unit,
                 timesamplingdownfactor,
                 samplingtime,
                 samplingtime_unit,
                 stokes,
                 numberofstations,
                 stations,
                 frequencydownsamplingfactor=None,
                 numberofcollapsedchannels=None,
                 channelwidth_frequency=None,
                 channelwidth_frequencyunit=None,
                 channelspersubband=None,
                 processingtype="Incoherent Stokes",
                 ):
        __stations = ltasip.Stations()
        for station in stations:
            __stations.append(station._get_pyxb_station(suppress_warning=True))

        __channelwidth=None
        if channelwidth_frequency and channelwidth_frequencyunit:
            __channelwidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit),

        self.__pyxb_rtprocessing=ltasip.IncoherentStokes(
            rawSamplingTime=ltasip.Time(rawsamplingtime, units=rawsamplingtime_unit),
			timeDownsamplingFactor=timesamplingdownfactor,
			samplingTime=ltasip.Time(samplingtime, units=samplingtime_unit),
            frequencyDownsamplingFactor=frequencydownsamplingfactor,
			numberOfCollapsedChannels=numberofcollapsedchannels,
            stokes=stokes,
		    numberOfStations=numberofstations,
            stations=__stations,
            #channelWidth=__channelwidth,
            channelsPerSubband=channelspersubband,
            processingType=processingtype
            )
        # Somehow this does not work in the constructor:
        self.__pyxb_rtprocessing.channelwidth=__channelwidth

    def _get_pyxb_rtprocessing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_rtprocessing

class FlysEyeProcessing():
    def __init__(self,
                 rawsamplingtime,
                 rawsamplingtime_unit,
                 timesamplingdownfactor,
                 samplingtime,
                 samplingtime_unit,
                 stokes,
                 channelwidth_frequency=None,
                 channelwidth_frequencyunit=None,
                 channelspersubband=None,
                 processingtype="Fly's Eye",
                 ):


        __channelwidth=None
        if channelwidth_frequency and channelwidth_frequencyunit:
             __channelwidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit)

        self.__pyxb_rtprocessing=ltasip.FlysEye(
                rawSamplingTime=ltasip.Time(rawsamplingtime, units=rawsamplingtime_unit),
                timeDownsamplingFactor=timesamplingdownfactor,
                samplingTime=ltasip.Time(samplingtime, units=samplingtime_unit),
                stokes=stokes,
               # channelWidth=__channelwidth,
                channelsPerSubband=channelspersubband,
                processingType=processingtype)

         # Somehow this does not work in the constructor:
        self.__pyxb_rtprocessing.channelwidth=__channelwidth


    def _get_pyxb_rtprocessing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_rtprocessing

class NonStandardProcessing():
    def __init__(self,
                 channelwidth_frequency,
                 channelwidth_frequencyunit,
                 channelspersubband,
                 processingtype="Non Standard"):

        self.__pyxb_rtprocessing=ltasip.NonStandard(
                channelsPerSubband=channelspersubband,
                processingType=processingtype,
                channelWidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit)
        )

    def _get_pyxb_rtprocessing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_rtprocessing


# ==============
# Processes:

class ProcessMap():
    def __init__(self,
                 strategyname,
                 strategydescription,
                 starttime,
                 duration,
                 identifier,
                 observation_identifier,
                 relations,
                 parset_identifier=None
                 ):

        __relations=ltasip.ProcessRelations()
        for rel in relations:
            __relations.append(rel._get_pyxb_processrelation(suppress_warning=True))
        self.process_map = dict(processIdentifier=identifier._get_pyxb_identifier(suppress_warning=True),
                                observationId=observation_identifier._get_pyxb_identifier(suppress_warning=True),
                                relations=__relations,
                                strategyName=strategyname, strategyDescription=strategydescription, startTime=starttime,
                                duration=duration)

        if parset_identifier:
            self.process_map["parset"]=parset_identifier._get_pyxb_identifier(suppress_warning=True)

    def get_dict(self):
        return self.process_map

class ProcessRelation():
    def __init__(self,
                 identifier,
                 type="GroupID"
    ):

        self.__pyxb_processrelation=ltasip.ProcessRelation(
            relationType=ltasip.ProcessRelationType(type),
            identifier=identifier._get_pyxb_identifier(suppress_warning=True)
        )

    def _get_pyxb_processrelation(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_processrelation


class SimpleProcess():
    def __init__(self, process_map):
        self.pyxb_process = ltasip.Process(**process_map.get_dict())

    def _get_pyxb_process(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.pyxb_process



# ########
# Others:

class PointingRaDec():

    def __init__(self,
                 ra_angle,
                 ra_angleunit,
                 dec_angle,
                 dec_angleunit,
                 equinox):

        self.__pyxb_pointing=ltasip.Pointing(
            rightAscension=ltasip.Angle(ra_angle, units=ra_angleunit),
            declination=ltasip.Angle(dec_angle, units=dec_angleunit),
            equinox=equinox)

    def _get_pyxb_pointing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pointing


class PointingAltAz():

    def __init__(self,
                 az_angle,
                 az_angleunit,
                 alt_angle,
                 alt_angleunit,
                 equinox):

        self.__pyxb_pointing=ltasip.Pointing(
            azimuth=ltasip.Angle(az_angle, units=az_angleunit),
            altitude=ltasip.Angle(alt_angle, units=alt_angleunit),
            equinox=equinox)

    def _get_pyxb_pointing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_pointing


class LinearAxis():
    def __init__(self,
                 number,
                 name,
                 units,
                 length,
                 increment,
                 referencepixel,
                 referencevalue):

        self.__pyxb_axis= ltasip.LinearAxis(
            number=number,
            name=name,
            units=units,
            length=length,
            increment=increment,
            referencePixel=referencepixel,
            referenceValue=referencevalue
        )
    def _get_pyxb_axis(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_axis


class TabularAxis():
    def __init__(self,
                 number,
                 name,
                 units,
                 length
    ):

        self.__pyxb_axis=ltasip.TabularAxis(
            number=number,
            name=name,
            units=units,
            length=length,
            )

    def _get_pyxb_axis(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_axis


class SubArrayPointing():
    def __init__(self,
                 pointing,
                 beamnumber,
                 identifier,
                 measurementtype,
                 targetname,
                 starttime,
                 duration,
                 numberofprocessing,
                 numberofcorrelateddataproducts,
                 numberofbeamformeddataproducts,
                 relations,
                 correlatorprocessing=None,
                 coherentstokesprocessing=None,
                 incoherentstokesprocessing=None,
                 flyseyeprocessing=None,
                 nonstandardprocessing=None,
                 measurementdescription=None):

        __relations=ltasip.ProcessRelations()
        for rel in relations:
            __relations.append(rel._get_pyxb_processrelation(suppress_warning=True))

        __processing=None
        for processing in [correlatorprocessing, coherentstokesprocessing, incoherentstokesprocessing, flyseyeprocessing, nonstandardprocessing]:
            if processing:
                if __processing is None:
                    __processing=ltasip.Processing()
                __processing.append(processing._get_pyxb_rtprocessing(suppress_warning=True)
                )


        self.__pyxb_subarraypointing = ltasip.SubArrayPointing(
            pointing=pointing._get_pyxb_pointing(suppress_warning=True),
            beamNumber=beamnumber,
            subArrayPointingIdentifier=identifier._get_pyxb_identifier(suppress_warning=True),
            measurementType=measurementtype,
            targetName=targetname,
            startTime=starttime,
            duration=duration,
            numberOfProcessing=numberofprocessing,
            numberOfCorrelatedDataProducts=numberofcorrelateddataproducts,
            numberOfBeamFormedDataProducts=numberofbeamformeddataproducts,
            processing=__processing,
            relations=__relations,
            measurementDescription=measurementdescription)

    def _get_pyxb_subarraypointing(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_subarraypointing


class Observation():
    def __init__(self,
                 observingmode,
                 instrumentfilter,
                 clock_frequency,
                 clock_frequencyunit,
                 stationselection,
                 antennaset,
                 timesystem,
                 numberofstations,
                 stations,
                 numberofsubarraypointings,
                 numberoftbbevents,
                 numberofcorrelateddataproducts,
                 numberofbeamformeddataproducts,
                 numberofbitspersample,
                 process_map,
                 channelwidth_frequency=None,
                 channelwidth_frequencyunit=None,
                 observationdescription=None,
                 channelspersubband=None,
                 subarraypointings=None,
                 transientbufferboardevents=None
    ):

        __stations = ltasip.Stations()
        for station in stations:
            __stations.append(station._get_pyxb_station(suppress_warning=True))

        __tbbevents=None
        if(transientbufferboardevents):
            __tbbevents = ltasip.TransientBufferBoardEvents()
            for source in transientbufferboardevents:
                __tbbevents.append(ltasip.TransientBufferBoardEvent(eventSource=source))

        __pointings=None
        if(subarraypointings):
            __pointings = ltasip.SubArrayPointings()
            for point in subarraypointings:
                __pointings.append(point._get_pyxb_subarraypointing(suppress_warning=True))

        self.__pyxb_observation = ltasip.Observation(
            observingMode=observingmode,
            instrumentFilter=instrumentfilter,
            clock=ltasip.ClockType(str(clock_frequency), units=clock_frequencyunit),
            stationSelection=stationselection,
            antennaSet=antennaset,
            timeSystem=timesystem,
            numberOfStations=numberofstations,
            stations=__stations,
            numberOfSubArrayPointings=numberofsubarraypointings,
            numberOftransientBufferBoardEvents=numberoftbbevents,
            numberOfCorrelatedDataProducts=numberofcorrelateddataproducts,
            numberOfBeamFormedDataProducts=numberofbeamformeddataproducts,
            numberOfBitsPerSample=numberofbitspersample,
            observationDescription=observationdescription,
            #channelWidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit),
            channelsPerSubband=channelspersubband,
            subArrayPointings=__pointings,
            transientBufferBoardEvents=__tbbevents,
            **process_map.get_dict()
        )

        # Somehow this does not work in the constructor:
        if channelwidth_frequency and channelwidth_frequencyunit:
            self.__pyxb_observation.channelwidth=ltasip.Frequency(channelwidth_frequency, units=channelwidth_frequencyunit),

    def _get_pyxb_observation(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__pyxb_observation




# #############################################################################################

# ============
# SIP document

class Sip(object):
    """
    The main Sip object. Instantiate this with the dataproduct you want to describe/ingest.
    Then add all related items to it, like observation, pipeline runs, and intermediate dataproducts. """

    print("\n################")
    print(VERSION)
    print("################\n")

    #-----------
    # Base document
    #---

    def __init__(self,
                 project_code,
                 project_primaryinvestigator,
                 project_contactauthor,
                 #project_telescope,
                 project_description,
                 dataproduct,
                 project_coinvestigators=None,
                 ):

        self.__sip = ltasip.ltaSip()

        self.__sip.sipGeneratorVersion = VERSION

        self.__sip.project = ltasip.Project(
            projectCode=project_code,
            primaryInvestigator=project_primaryinvestigator,
            contactAuthor=project_contactauthor,
            telescope="LOFAR",#project_telescope,
            projectDescription=project_description,
            coInvestigator=project_coinvestigators,
            )

        self.__sip.dataProduct=dataproduct._get_pyxb_dataproduct(suppress_warning=True)

        self.get_prettyxml() # for validation

    @classmethod
    def from_xml(cls, xml):
        """
        If you are processing data that is already described by a SIP (e.g. LTA data), you can instantiate a Sip object
        from that SIP XML string. When adding related dataproducts based on the SIP that describes it, this add all the
        SIP content to your new SIP. This way, you only have to fill in the gaps, e.g. add your pipeline run.

        -> add_related_dataproduct_with_history()
        """
        newsip = Sip.__new__(Sip)
        newsip._set_pyxb_sip(ltasip.CreateFromDocument(xml), suppress_warning=True)
        newsip.get_prettyxml() # for validation
        return newsip

    def _get_pyxb_sip(self, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        return self.__sip

    def _set_pyxb_sip(self, pyxb_sip, suppress_warning=False):
        if not suppress_warning:
            print_user_warning()
        self.__sip = pyxb_sip


    #-------------
    # Optional additions
    #---

    def add_related_dataproduct(self, dataproduct):
        self.__sip.relatedDataProduct.append(dataproduct._get_pyxb_dataproduct(suppress_warning=True))
        return self.get_prettyxml()

    def add_observation(self, observation):
        self.__sip.observation.append(observation._get_pyxb_observation(suppress_warning=True))
        return self.get_prettyxml()


    def add_pipelinerun(self, pipeline):
        self.__sip.pipelineRun.append(pipeline._get_pyxb_pipeline(suppress_warning=True))
        return self.get_prettyxml()


    def add_unspecifiedprocess(self,
                               observingmode,
                               description,
                               process_map,
                               ):

        up = ltasip.UnspecifiedProcess(
            observingMode=observingmode,
            description=description,
            **process_map.get_dict()
        )
        self.__sip.unspecifiedProcess.append(up)

        return self.get_prettyxml()


    def add_parset(self,
                   identifier,
                   contents):

        self.__sip.parset.append(ltasip.Parset(
            identifier=identifier._get_pyxb_identifier(suppress_warning=True),
            contents=contents
        ))

        return self.get_prettyxml()

    def add_related_dataproduct_with_history(self, relateddataproduct_sip):
        # add the dataproduct described by the SIP (if not there)
        if not any(x.dataProductIdentifier.identifier == relateddataproduct_sip.__sip.dataProduct.dataProductIdentifier.identifier for x in self.__sip.relatedDataProduct):
            self.__sip.relatedDataProduct.append(relateddataproduct_sip.__sip.dataProduct)
        else:
            print("WARNING: There already exists a dataproduct with id", relateddataproduct_sip.__sip.dataProduct.dataProductIdentifier.identifier," - Will try to add any new related items anyway.")
        if relateddataproduct_sip.__sip.relatedDataProduct:
            # add related dataproducts (if not there already)
            for dp in relateddataproduct_sip.__sip.relatedDataProduct:
                if not any(x.dataProductIdentifier.identifier == dp.dataProductIdentifier.identifier for x in self.__sip.relatedDataProduct):
                    self.__sip.relatedDataProduct.append(dp)
        if relateddataproduct_sip.__sip.observation:
            # add related dataproducts (if not there already)
            for obs in relateddataproduct_sip.__sip.observation:
                if not any(x.processIdentifier.identifier == obs.processIdentifier.identifier for x in self.__sip.observation):
                    self.__sip.observation.append(obs)
        if relateddataproduct_sip.__sip.pipelineRun:
            # add related pipelineruns (if not there already)
            for pipe in relateddataproduct_sip.__sip.pipelineRun:
                if not any(x.processIdentifier.identifier == pipe.processIdentifier.identifier for x in self.__sip.pipelineRun):
                    self.__sip.pipelineRun.append(pipe)
        if relateddataproduct_sip.__sip.unspecifiedProcess:
            # add related unspecified processes (if not there already)
            for unspec in relateddataproduct_sip.__sip.unspecifiedProcess:
                if not any(x.processIdentifier.identifier == unspec.processIdentifier.identifier for x in self.__sip.unspecifiedProcess):
                    self.__sip.unspecifiedProcess.append(unspec)
        if relateddataproduct_sip.__sip.parset:
            # add related parsets (if not there already)
            for par in relateddataproduct_sip.__sip.parset:
                if not any(x.identifier.identifier == par.identifier.identifier for x in self.__sip.parset):
                    self.__sip.parset.append(par)
        return self.get_prettyxml()


    def get_dataproduct_identifier(self):
        """
        Get the identifier of the dataproduct that is described by this Sip, e.g. for reference by your pipeline run..
        """
        identifier = Identifier.__new__(Identifier)
        identifier._set_pyxb_identifier(self.__sip.dataProduct.dataProductIdentifier, suppress_warning=True)
        return identifier

    def get_dataproduct_subarraypointing_identifier(self):
        dataproduct = self.__sip.dataProduct
        if isinstance(dataproduct, ltasip.CorrelatedDataProduct):
            identifier = Identifier.__new__(Identifier)
            identifier._set_pyxb_identifier(dataproduct.subArrayPointingIdentifier, suppress_warning=True)
            return identifier
        else:
            raise Exception("This SIP does not describe a correlated dataproduct. No subarray pointing available.")

    # this will also validate the document so far
    def get_prettyxml(self):
        try:
            dom = self.__sip.toDOM()
            #print "1) "+dom.toprettyxml()
            dom.documentElement.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            dom.documentElement.setAttribute('xsi:schemaLocation', "http://www.astron.nl/SIP-Lofar LTA-SIP-2.7.0.xsd")
            #print "2) "+dom.toprettyxml()
            return dom.toprettyxml()
        except pyxb.ValidationError as err:
            #print str(err)
            print(err.details())
            raise err

    def prettyprint(self):
        print(self.get_prettyxml())


    def save_to_file(self, path):
        path = os.path.expanduser(path)
        with open(path, 'w+') as f:
            f.write(self.get_prettyxml())

