#!/usr/bin/env python3

# Copyright (C) 2012-2015    ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

# $Id: $

import unittest

try:
    import pyxb
except ImportError as e:
    print(str(e))
    print('Please install python3 package pyxb: sudo apt-get install python3-pyxb')
    exit(3)    # special lofar test exit code: skipped test

from lofar.lta.sip import siplib
from lofar.lta.sip import validator
from lofar.lta.sip import constants
import os

# d = os.path.dirname(os.path.realpath(__file__))
TMPFILE_PATH = "/tmp/test_siplib.xml"
RELATEDSIP = '/tmp/sipfrommom.xml'    # todo: how to deploy in testdir?

dp_id = siplib.Identifier("test")
in_dpid1 = siplib.Identifier("test")
in_dpid2 = siplib.Identifier("test")
proc_id = siplib.Identifier("test")
pipe_id = siplib.Identifier("test")
obs_id = siplib.Identifier("test")
point_id = siplib.Identifier("test")

def create_basicdoc():
    return siplib.Sip(
            project_code = "code",
            project_primaryinvestigator = "pi",
            project_contactauthor = "coauthor",
            # project_telescope="LOFAR",
            project_description = "awesome project",
            project_coinvestigators = ["sidekick1", "sidekick2"],
            dataproduct = siplib.SimpleDataProduct(
                siplib.DataProductMap(
                    type = "Unknown",
                    identifier = dp_id,
                    size = 1024,
                    filename = "/home/paulus/test.h5",
                    fileformat = "HDF5",
                    process_identifier = pipe_id,
                    checksum_md5 = "hash1",
                    checksum_adler32 = "hash2",
                    storageticket = "ticket"
                )
            )
        )

def create_processmap():
    return siplib.ProcessMap(
                strategyname = "strategy1",
                strategydescription = "awesome strategy",
                starttime = "1980-03-23T10:20:15",
                duration = "P6Y3M10DT15H",
                identifier = proc_id,
                observation_identifier = obs_id,
                parset_identifier = siplib.Identifier("test"),
                relations = [
                    siplib.ProcessRelation(
                        identifier = siplib.Identifier("test"),
                    ),
                    siplib.ProcessRelation(
                        identifier = siplib.Identifier("test"),
                    )
                ]
            )

def create_pipelinemap():
    return siplib.PipelineMap(
                    name = "simple",
                    version = "version",
                    sourcedata_identifiers = [in_dpid1, in_dpid2],
                    process_map = create_processmap(),
                )

def create_dataproductmap():
    return siplib.DataProductMap(
                    type = "Unknown",
                    identifier = dp_id,
                    size = 2048,
                    filename = "/home/paulus/test.h5",
                    fileformat = "HDF5",
                    process_identifier = proc_id,
                )

class TestSIPlib(unittest.TestCase):

    def test_basic_doc(self):
        # create example doc with mandatory attributes
        print("===\nCreating basic document:\n")
        mysip = create_basicdoc()
        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

    def test_dataproducts(self):
        mysip = create_basicdoc()
        print("===\nAdding related generic dataproduct:\n")
        # add optional dataproduct item
        print(mysip.add_related_dataproduct(
            siplib.GenericDataProduct(
                create_dataproductmap()
            )
        ))

        # add optional dataproduct item
        print("===\nAdding related pulp summary dataproduct:\n")
        print(mysip.add_related_dataproduct(
            siplib.PulpSummaryDataProduct(
                create_dataproductmap(),
                filecontent = ["content_a", "content_b"],
                datatype = "CoherentStokes"
            )
        ))

        # add optional dataproduct item
        print("===\nAdding related pulp dataproduct:\n")
        print(mysip.add_related_dataproduct(
            siplib.PulpDataProduct(
                create_dataproductmap(),
                filecontent = ["content_a", "content_b"],
                datatype = "CoherentStokes",
                arraybeam = siplib.SimpleArrayBeam(siplib.ArrayBeamMap(
                    subarraypointing_identifier = point_id,
                    beamnumber = 4,
                    dispersionmeasure = 16,
                    numberofsubbands = 3,
                    stationsubbands = [1, 2, 3],
                    samplingtime = 3,
                    samplingtimeunit = "ms",
                    centralfrequencies = "",
                    centralfrequencies_unit = "MHz",
                    channelwidth_frequency = 160,
                    channelwidth_frequencyunit = "MHz",
                    channelspersubband = 5,
                    stokes = ["I", "Q"]
                ))
            )
        ))

        # add optional dataproduct item
        print("===\nAdding related beamformed dataproduct:\n")
        print(mysip.add_related_dataproduct(
            siplib.BeamFormedDataProduct(
                create_dataproductmap(),
                beams = [siplib.FlysEyeBeam(
                    arraybeam_map = siplib.ArrayBeamMap(
                        subarraypointing_identifier = point_id,
                        beamnumber = 4,
                        dispersionmeasure = 16,
                        numberofsubbands = 3,
                        stationsubbands = [1, 2, 3],
                        samplingtime = 3,
                        samplingtimeunit = "ms",
                        centralfrequencies = "",
                        centralfrequencies_unit = "MHz",
                        channelwidth_frequency = 160,
                        channelwidth_frequencyunit = "MHz",
                        channelspersubband = 5,
                        stokes = ["I", "Q"]),
                    station = siplib.Station.preconfigured("CS001", ["HBA0", "HBA1"])
                )]
            )
        ))

        # add optional dataproduct item
        print("===\nAdding related sky image dataproduct:\n")
        print(mysip.add_related_dataproduct(
            siplib.SkyImageDataProduct(
                create_dataproductmap(),
                numberofaxes = 2,
                coordinates = [
                    siplib.SpectralCoordinate(
                        quantity_type = "Frequency",
                        quantity_value = 20.0,
                        axis = siplib.LinearAxis(
                            number = 5,
                            name = "bla",
                            units = "parsec",
                            length = 5,
                            increment = 5,
                            referencepixel = 7.5,
                            referencevalue = 7.4)),
                    siplib.SpectralCoordinate(
                        quantity_type = "Frequency",
                        quantity_value = 20.0,
                        axis = siplib.TabularAxis(
                            number = 5,
                            name = "bla",
                            units = "parsec",
                            length = 5,
                            )),
                    siplib.DirectionCoordinate(
                        linearaxis_a = siplib.LinearAxis(
                            number = 5,
                            name = "bla",
                            units = "parsec",
                            length = 5,
                            increment = 5,
                            referencepixel = 7.5,
                            referencevalue = 7.4),
                        linearaxis_b = siplib.LinearAxis(
                            number = 5,
                            name = "bla",
                            units = "parsec",
                            length = 5,
                            increment = 5,
                            referencepixel = 7.5,
                            referencevalue = 7.4),
                        pc0_0 = 0.0,
                        pc0_1 = 0.1,
                        pc1_0 = 1.0,
                        pc1_1 = 1.1,
                        equinox = "SUN",
                        radecsystem = "ICRS",
                        projection = "rear",
                        projectionparameters = [1.0, 1.0, 1.0],
                        longitudepole_angle = 1.0,
                        longitudepole_angleunit = "degrees",
                        latitudepole_angle = 2.0,
                        latitudepole_angleunit = "degrees",
                        ),
                    siplib.PolarizationCoordinate(
                        tabularaxis = siplib.TabularAxis(
                            number = 5,
                            name = "bla",
                            units = "parsec",
                            length = 5,
                            ),
                        polarizations = ["I", "YY", "XX", "Q"]
                    ),
                    siplib.TimeCoordinate(
                        equinox = "SUN",
                        axis = siplib.TabularAxis(
                            number = 5,
                            name = "timetabular",
                            units = "parsec",
                            length = 5,
                            ),
                        )
                ],
                locationframe = "GEOCENTER",
                timeframe = "timeframe",
                observationpointing = siplib.PointingRaDec(
                    ra_angle = 1.0,
                    ra_angleunit = "degrees",
                    dec_angle = 42.0,
                    dec_angleunit = "degrees",
                    equinox = "SUN"
                ),
                restoringbeammajor_angle = 1.0,
                restoringbeammajor_angleunit = "degrees",
                restoringbeamminor_angle = 2.0,
                restoringbeamminor_angleunit = "degrees",
                rmsnoise = 1.0
            )
        ))

        # add optional dataproduct item
        print("===\nAdded related correlated dataproduct:\n")
        print(mysip.add_related_dataproduct(
            siplib.CorrelatedDataProduct(
                create_dataproductmap(),
                subarraypointing_identifier = siplib.Identifier("test"),
                subband = "1",
                starttime = "1980-03-23T10:20:15",
                duration = "P6Y3M10DT15H",
                integrationinterval = 10,
                integrationintervalunit = "ms",
                central_frequency = 160,
                central_frequencyunit = "MHz",
                channelwidth_frequency = 200,
                channelwidth_frequencyunit = "MHz",
                channelspersubband = 122,
                stationsubband = 2,
                )
        ))

        # add optional dataproduct item
        print("===\nAdding related pixelmap dataproduct:\n")
        print(mysip.add_related_dataproduct(
            siplib.PixelMapDataProduct(
                create_dataproductmap(),
                numberofaxes = 5,
                coordinates = [siplib.SpectralCoordinate(
                    quantity_type = "Frequency",
                    quantity_value = 20.0,
                    axis = siplib.LinearAxis(
                        number = 5,
                        name = "bla",
                        units = "parsec",
                        length = 5,
                        increment = 5,
                        referencepixel = 7.5,
                        referencevalue = 7.4))]
            )
        ))

        # add optional dataproduct item
        print("===\nAdding related pixelmap dataproduct using predefined constants:\n")
        print(mysip.add_related_dataproduct(
            siplib.SkyImageDataProduct(
                create_dataproductmap(),
                numberofaxes = 2,
                coordinates = [
                    siplib.SpectralCoordinate(
                        quantity_type = constants.SPECTRALQUANTITYTYPE_VELOCITYAPPRADIAL,
                        quantity_value = 20.0,
                        axis = siplib.LinearAxis(
                            number = 5,
                            name = "bla",
                            units = "unit",
                            length = 5,
                            increment = 5,
                            referencepixel = 7.5,
                            referencevalue = 7.4)),
                    siplib.DirectionCoordinate(
                        linearaxis_a = siplib.LinearAxis(
                            number = 5,
                            name = "bla",
                            units = "unit",
                            length = 5,
                            increment = 5,
                            referencepixel = 7.5,
                            referencevalue = 7.4),
                        linearaxis_b = siplib.LinearAxis(
                            number = 5,
                            name = "blb",
                            units = "unit",
                            length = 5,
                            increment = 5,
                            referencepixel = 7.5,
                            referencevalue = 7.4),
                        pc0_0 = 0.0,
                        pc0_1 = 0.1,
                        pc1_0 = 1.0,
                        pc1_1 = 1.1,
                        equinox = constants.EQUINOXTYPE_JUPITER,
                        radecsystem = constants.RADECSYSTEM_FK4_NO_E,
                        projection = "rear",
                        projectionparameters = [1.0, 1.0, 1.0],
                        longitudepole_angle = 1.0,
                        longitudepole_angleunit = constants.ANGLEUNIT_RADIANS,
                        latitudepole_angle = 2.0,
                        latitudepole_angleunit = constants.ANGLEUNIT_ARCSEC,
                        ),
                    siplib.PolarizationCoordinate(
                        tabularaxis = siplib.TabularAxis(
                            number = 5,
                            name = "bla",
                            units = "someunit",
                            length = 5,
                            ),
                        polarizations = [constants.POLARIZATIONTYPE_LR, constants.POLARIZATIONTYPE_XRE]
                    ),
                ],
                locationframe = constants.LOCATIONFRAME_LOCAL_GROUP,
                timeframe = "timeframe",
                observationpointing = siplib.PointingRaDec(
                    ra_angle = 1.0,
                    ra_angleunit = constants.ANGLEUNIT_DEGREES,
                    dec_angle = 42.0,
                    dec_angleunit = constants.ANGLEUNIT_DEGREES,
                    equinox = constants.EQUINOXTYPE_B1950
                ),
                restoringbeammajor_angle = 1.0,
                restoringbeammajor_angleunit = constants.ANGLEUNIT_DEGREES,
                restoringbeamminor_angle = 2.0,
                restoringbeamminor_angleunit = constants.ANGLEUNIT_DEGREES,
                rmsnoise = 1.0
            )
        ))
        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

    def test_observation(self):
        mysip = create_basicdoc()
        # add optional observation item
        print("===\nAdding observation:\n")
        print(mysip.add_observation(siplib.Observation(observingmode = "Interferometer",
                                    instrumentfilter = "10-70 MHz",
                                    clock_frequency = '160',
                                    clock_frequencyunit = "MHz",
                                    stationselection = "Core",
                                    antennaset = "HBA Zero",
                                    timesystem = "UTC",
                                    stations = [siplib.Station.preconfigured("RS106", ["LBA"]),
                                              siplib.Station.preconfigured("DE609", ["HBA"])],
                                    numberofstations = 5,
                                    numberofsubarraypointings = 5,
                                    numberoftbbevents = 5,
                                    numberofcorrelateddataproducts = 5,
                                    numberofbeamformeddataproducts = 5,
                                    numberofbitspersample = 5,
                                    process_map = create_processmap(),
                                    observationdescription = "description",
                                    channelwidth_frequency = 160,
                                    channelwidth_frequencyunit = "MHz",
                                    channelspersubband = 5,
                                    subarraypointings = [siplib.SubArrayPointing(
                                        pointing = siplib.PointingAltAz(
                                            az_angle = 20,
                                            az_angleunit = "degrees",
                                            alt_angle = 30,
                                            alt_angleunit = "degrees",
                                            equinox = "SUN"
                                        ),
                                        beamnumber = 5,
                                        identifier = point_id,
                                        measurementtype = "All Sky",
                                        targetname = "Sun",
                                        starttime = "1980-03-23T10:20:15",
                                        duration = "P6Y3M10DT15H",
                                        numberofprocessing = 1,
                                        numberofcorrelateddataproducts = 2,
                                        numberofbeamformeddataproducts = 1,
                                        relations = [siplib.ProcessRelation(
                                            identifier = siplib.Identifier("test")
                                        )],
                                        correlatorprocessing = siplib.CorrelatorProcessing(
                                            integrationinterval = 0.5,
                                            integrationinterval_unit = "ns",
                                            channelwidth_frequency = 160,
                                            channelwidth_frequencyunit = "MHz"
                                        ),
                                        coherentstokesprocessing = siplib.CoherentStokesProcessing(
                                            rawsamplingtime = 20,
                                            rawsamplingtime_unit = "ns",
                                            timesamplingdownfactor = 2,
                                            samplingtime = 10,
                                            samplingtime_unit = "ns",
                                            stokes = ["XX"],
                                            numberofstations = 1,
                                            stations = [siplib.Station.preconfigured("CS002", ["HBA0", "HBA1"])],
                                            frequencydownsamplingfactor = 2,
                                            numberofcollapsedchannels = 2,
                                            channelwidth_frequency = 160,
                                            channelwidth_frequencyunit = "MHz",
                                            channelspersubband = 122
                                        ),
                                        incoherentstokesprocessing = siplib.IncoherentStokesProcessing(
                                            rawsamplingtime = 20,
                                            rawsamplingtime_unit = "ns",
                                            timesamplingdownfactor = 2,
                                            samplingtime = 10,
                                            samplingtime_unit = "ns",
                                            stokes = ["XX"],
                                            numberofstations = 1,
                                            stations = [siplib.Station.preconfigured("CS003", ["HBA0", "HBA1"])],
                                            frequencydownsamplingfactor = 2,
                                            numberofcollapsedchannels = 2,
                                            channelwidth_frequency = 160,
                                            channelwidth_frequencyunit = "MHz",
                                            channelspersubband = 122
                                        ),
                                        flyseyeprocessing = siplib.FlysEyeProcessing(
                                            rawsamplingtime = 10,
                                            rawsamplingtime_unit = "ms",
                                            timesamplingdownfactor = 2,
                                            samplingtime = 2,
                                            samplingtime_unit = "ms",
                                            stokes = ["I"],
                                            ),
                                        nonstandardprocessing = siplib.NonStandardProcessing(
                                            channelwidth_frequency = 160,
                                            channelwidth_frequencyunit = "MHz",
                                            channelspersubband = 122
                                        )
                                    )],
                                    transientbufferboardevents = ["event1", "event2"]
                                )))

        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

    def test_parset(self):
         mysip = create_basicdoc()
         print("===\nAdding parset:\n")
         print(mysip.add_parset(
             identifier = siplib.Identifier("test"),
             contents = "blabla"))

         mysip.save_to_file(TMPFILE_PATH)
         self.assertTrue(validator.validate(TMPFILE_PATH))

    def test_unspecifiedprocess(self):
        mysip = create_basicdoc()
        print("===\nAdding unspecified process:\n")
        print(mysip.add_unspecifiedprocess(
            observingmode = "Interferometer",
            description = "unspecified",
            process_map = create_processmap()
        ))
        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

    def test_pipelines(self):
        mysip = create_basicdoc()
        print("===\nAdding simple pipelinerun:\n")
        print(mysip.add_pipelinerun(
            siplib.SimplePipeline(
                create_pipelinemap()
            )
        ))

        print("===\nAdding generic pipelinerun:\n")
        print(mysip.add_pipelinerun(
            siplib.GenericPipeline(
                create_pipelinemap()
            )
        ))

        print("===\nAdding cosmic ray pipelinerun:\n")
        print(mysip.add_pipelinerun(
            siplib.CosmicRayPipeline(
                create_pipelinemap()
            )
        ))

        print("===\nAdding long baseline pipelinerun:\n")
        print(mysip.add_pipelinerun(
            siplib.LongBaselinePipeline(
                create_pipelinemap(),
                subbandspersubbandgroup = 5,
                subbandgroupspermS = 5

            )
        ))

        print("===\nAdding imaging pipelinerun:\n")
        print(mysip.add_pipelinerun(siplib.ImagingPipeline(
             create_pipelinemap(),
             imagerintegrationtime = 10,
             imagerintegrationtime_unit = "ms",
             numberofmajorcycles = 5,
             numberofinstrumentmodels = 5,
             numberofcorrelateddataproducts = 1,
             numberofskyimages = 1,
        )
        ))

        print("===\nAdding calibration pipelinerun:\n")
        print(mysip.add_pipelinerun(
            siplib.CalibrationPipeline(
            create_pipelinemap(),
            skymodeldatabase = "db",
            numberofinstrumentmodels = 1,
            numberofcorrelateddataproducts = 1,
            frequencyintegrationstep = 1,
            timeintegrationstep = 1,
            flagautocorrelations = True,
            demixing = False
        )))

        print("===\nAdding averaging pipelinerun:\n")
        print(mysip.add_pipelinerun(
            siplib.AveragingPipeline(
            create_pipelinemap(),
            numberofcorrelateddataproducts = 1,
            frequencyintegrationstep = 1,
            timeintegrationstep = 1,
            flagautocorrelations = True,
            demixing = False
        )))

        print("===\nAdding pulsar pipelinerun:\n")
        print(mysip.add_pipelinerun(
            siplib.PulsarPipeline(
                create_pipelinemap(),
                pulsarselection = "Pulsars in observation specs, file and brightest in SAP and TAB",
                pulsars = ["J1234+67"],
                dosinglepulseanalysis = False,
                convertRawTo8bit = True,
                subintegrationlength = 10,
                subintegrationlength_unit = 'ns',
                skiprfiexcision = False,
                skipdatafolding = False,
                skipoptimizepulsarprofile = True,
                skipconvertrawintofoldedpsrfits = False,
                runrotationalradiotransientsanalysis = True,
                skipdynamicspectrum = False,
                skipprefold = True
            )
        ))

        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

    def test_add_sip(self):
        # create example doc with mandatory attributes
        mysip = create_basicdoc()
        with open(RELATEDSIP) as f:
            xml = f.read()
        sip = siplib.Sip.from_xml(xml)
        mysip.add_related_dataproduct_with_history(sip)
        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

# run tests if main
if __name__ == '__main__':
    unittest.main()
