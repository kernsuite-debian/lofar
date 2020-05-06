#!/usr/bin/env python3

import sys
import pprint
from . import siplib
from . import constants
from ast import literal_eval
import datetime
import copy
import uuid


class Feedback():

    def __init__(self, feedback):
        self.__inputstrings = feedback
        self.__tree = {}
        print("parsing",len(feedback),"lines of feedback")
        for line in feedback:
            if line.strip() and not line.startswith("#"):
                try:
                    key, value = line.split('=')
                    t = self.__tree
                    if value.strip():
                        for item in key.split('.')[:-1]:
                            #if not item == "ObsSW" and not item == "Observation" and not item == "DataProducts": //todo: check if the hierarchy can/should be flattened. Will leave this for now. -> Probably more flexible to use a configurable the prefix
                            t = t.setdefault(item, {})
                        try:
                            t[key.split('.')[-1]] = value.strip().replace("\"","")
                        except:
                            t[key.split('.')[-1]] = value.strip()
                except:
                    print("Skipping line:", line)

        # Now self.__tree holds nested dicts according to the dot-encoded key hierarchy
        #pprint.pprint(self.__tree)

    # Returns a basic SIP document with the project details from the feedback and the provided dataproduct
    # E.g. by providing the all self.__tree.get("ObsSW").get("Observation").get("Dataproducts")
    def __get_basic_sip(self, dataproduct):
        campaign = self.__tree.get("ObsSW").get("Observation").get("Campaign") #todo: check whether this is always available

        sip = siplib.Sip(
            project_code=campaign.get("name"),
            project_primaryinvestigator=campaign.get("PI"),
            project_contactauthor=campaign.get("contact"),
            project_description=campaign.get("title"),
            dataproduct=dataproduct,
            project_coinvestigators=[campaign.get("CO_I")]
        )

        return sip

    # determine duration in ISO format (couldn't find a nice lib for it)
    def __convert_timedelta_to_iso(self, td):
        y,w,d,h,m,s = td.days//365, (td.days//7)%365, (td.days//7)%7, td.seconds//3600, (td.seconds//60)%60, td.seconds%60
        duration = 'P{}Y{}M{}DT{}H{}M{}S'.format(y,w,d,h,m,s)
        return duration

    # return dataproducts objects from 'pseudo feedback', which can be generated from the MS's by some existing code.
    def get_dataproducts(self,
                         prefix="ObsSW.Observation",
                         identifier_source='test',
                         process_identifier=None,
                         subarraypointing_identifier=None,
                         ):

        if process_identifier is None:
            process_identifier = siplib.Identifier(identifier_source)
        if subarraypointing_identifier is None:
            subarraypointing_identifier = siplib.Identifier(identifier_source)

        prefixes = prefix.split(".")
        dps = self.__get_tree_elem(prefix)

        #print dps.items()

        dataproducts = []
        dps = [(k, dp) for (k, dp) in list(dps.items()) if k.startswith("Output_")]
        for k, dp in dps:

            print("Parsing",k,"...")

            # correct timestamp format
            startt=dp.get("startTime")
            if len(startt.strip().split()) == 2:
                startt=startt.replace(' ','T', 1)

            if k.startswith("Output_Correlated_["):
              dataproducts.append(
                siplib.CorrelatedDataProduct(
                siplib.DataProductMap(
                    type="Correlator data",
                    identifier=siplib.Identifier(identifier_source),
                    size=dp.get("size"),
                    filename=dp.get("filename"),
                    fileformat=dp.get("fileFormat"),
                    process_identifier=process_identifier,
                ),
                subarraypointing_identifier=subarraypointing_identifier,
                subband=dp.get("subband"),
                starttime=startt,
                duration=self.__convert_timedelta_to_iso(datetime.timedelta(seconds=float(dp.get("duration")))),
                integrationinterval=dp.get("integrationInterval"),
                integrationintervalunit=constants.TIMEUNIT_S, #todo:check!
                central_frequency=dp.get("centralFrequency"),
                central_frequencyunit=constants.FREQUENCYUNIT_HZ, #todo:check!
                channelwidth_frequency=dp.get("channelWidth"), # todo:check!
                channelwidth_frequencyunit=constants.FREQUENCYUNIT_HZ, # todo:check!
                channelspersubband=dp.get("channelsPerSubband"),
                stationsubband=dp.get("stationSubband"),
                )
            )
            elif k.startswith("Output_Beamformed_["):
                beamlist=None

                dataproduct = siplib.BeamFormedDataProduct(
                    siplib.DataProductMap(
                        type="Correlator data",
                        identifier=siplib.Identifier('identifier_source'),
                        size=dp.get("size"),
                        filename=dp.get("filename"),
                        fileformat=dp.get("fileFormat"),
                        process_identifier=process_identifier
                    ),
                    beams=beamlist
                    )

        # todo other dataproduct types (if helpful, this is kind of prefactor specific for now)
        return dataproducts


    def __get_tree_elem(self, prefix):
        prefixes = prefix.split(".")
        elem = self.__tree
        for prefix in prefixes:
            if elem.get(prefix):
                elem = elem.get(prefix)
            else:
                print("provided prefix seems to be wrong: '"+prefix+"' not in", list(elem.keys()))
        return elem


    # Returns sips for all output dataproducts in this feedback.
    # todo: Re-evaluate the design! Does this setup really make sense? Since the relevant IDs of items that are already
    # todo: ...in the catalog are not part of the feedback, SIPs of related dataproducts (incl. observation info) have
    # todo: ...to be queried from the catalog anyway and hence that info does not have to be parsed from the feedback.
    # todo: ...Instead, for each SIP, only the output dataproduct and the new process should be parsed.
    # todo: ...The only application for parsing all info that I see is, when observations happen outside of MoM control
    # todo: ...and are not present with an existing ID in the LTA. In that case we could apply e.g. some UUID.
    # todo: After evaluation, if still applicable, check assumptions made for missing attributes, assign new IDs, etc.
    def get_dataproduct_sips(self, obs_prefix="ObsSW.Observation", dp_prefix="ObsSW.Observation.DataProducts"):

        print("Generating SIPs for all dataproducts")

        obs = self.__get_tree_elem(obs_prefix)
        dps = self.__get_tree_elem(dp_prefix)

        campaign = obs.get("Campaign")

        antennaset = obs.get("antennaSet").split("_")[0]+" "+obs.get("antennaSet").split("_")[1].title()
        antennafields = obs.get("antennaArray").split(";")
        stations = []
        y = obs.get("VirtualInstrument").get("stationList").replace("[","").replace("]","").split(",")
        for x in y:
            stations.append(siplib.Station.preconfigured(str(x),antennafields))


        # determine duration in ISO format (couldn't find a nice lib for it)
        td= (datetime.datetime.strptime(obs.get("stopTime"),"%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(obs.get("startTime"),"%Y-%m-%d %H:%M:%S"))
        duration = self.__convert_timedelta_to_iso(td)


        #---optional items:
        # todo: online processing
        # todo: -> if these are present, add to sip, else set None
        # correlatorprocessing=siplib.CorrelatorProcessing(
        #     integrationinterval=0.5,
        #     integrationinterval_unit="ns",
        #     channelwidth_frequency=160,
        #     channelwidth_frequencyunit="MHz"
        # ),
        # coherentstokesprocessing=siplib.CoherentStokesProcessing(
        #     rawsamplingtime=20,
        #     rawsamplingtime_unit="ns",
        #     timesamplingdownfactor=2,
        #     samplingtime=10,
        #     samplingtime_unit="ns",
        #     stokes=["XX"],
        #     numberofstations=1,
        #     stations=[siplib.Station.preconfigured("CS002",["HBA0","HBA1"])],
        #     frequencydownsamplingfactor=2,
        #     numberofcollapsedchannels=2,
        #     channelwidth_frequency=160,
        #     channelwidth_frequencyunit="MHz",
        #     channelspersubband=122
        # ),
        # incoherentstokesprocessing=siplib.IncoherentStokesProcessing(
        #     rawsamplingtime=20,
        #     rawsamplingtime_unit="ns",
        #     timesamplingdownfactor=2,
        #     samplingtime=10,
        #     samplingtime_unit="ns",
        #     stokes=["XX"],
        #     numberofstations=1,
        #     stations=[siplib.Station.preconfigured("CS003",["HBA0","HBA1"])],
        #     frequencydownsamplingfactor=2,
        #     numberofcollapsedchannels=2,
        #     channelwidth_frequency=160,
        #     channelwidth_frequencyunit="MHz",
        #     channelspersubband=122
        # ),
        # flyseyeprocessing=siplib.FlysEyeProcessing(
        #     rawsamplingtime=10,
        #     rawsamplingtime_unit="ms",
        #     timesamplingdownfactor=2,
        #     samplingtime=2,
        #     samplingtime_unit="ms",
        #     stokes=["I"],
        #     ),
        # nonstandardprocessing=siplib.NonStandardProcessing(
        #     channelwidth_frequency=160,
        #     channelwidth_frequencyunit="MHz",
        #     channelspersubband=122
        # )
        #---

        # Determine pointings:
        pointings=[]
        for key in (k for k,v in list(obs.items()) if k.startswith("Beam[")):
            beam = obs.get(key)

            point=siplib.PointingAltAz(         #todo: check if always azel pointing or check on "directionType"
                                                az_angle=beam.get("angle1"),
                                                az_angleunit=constants.ANGLEUNIT_RADIANS,
                                                alt_angle=beam.get("angle2"),
                                                alt_angleunit=constants.ANGLEUNIT_RADIANS,
                                                equinox=constants.EQUINOXTYPE_J2000, #beam.get("directionType") # todo: Is this the right value?
            )
            #todo elif the thousand other directionType options... conversion needed?

            if beam.get("startTime"):
                starttime = beam.get("startTime").replace(" ","T") #todo: add to obs starttime ?!
            else:
                starttime = obs.get("startTime").replace(" ","T")

            if beam.get("duration") == "0":
                dur = duration
            else:
                dur = int(beam.get("duration"))

            pointings.append(
                siplib.SubArrayPointing(
                    pointing = point,
                    beamnumber=key.split("[")[1].split("]")[0],
                    identifier=siplib.Identifier(source="test"), # todo: build correct subyarray pointing identifier form beam.monId
                    measurementtype=constants.MEASUREMENTTYPE_TARGET, # todo
                    targetname=beam.get("target"),
                    starttime=starttime,
                    duration=dur,
                    numberofprocessing=1, # todo
                    numberofcorrelateddataproducts=2,  # todo
                    numberofbeamformeddataproducts=1,  # todo
                    relations=[siplib.ProcessRelation(
                        identifier=siplib.Identifier('test') # todo
                        )],
                        #todo: optional kwargs
                    )
                )

        # create sip for each dataproduct
        sips = {}
        for dataproduct in self.get_dataproducts(prefix=dp_prefix):
            try:
                filename = dataproduct.get_pyxb_dataproduct().fileName
                print("Creating SIP for", filename)

                # create SIP document for dataproduct
                sip = self.__get_basic_sip(dataproduct)
                tbbevents=[] #["event1","event2"] #todo

                # add the observation for this dataproduct
                # todo: Put observations in separate parser function get_observations(), same for other items.
                sip.add_observation(
                    siplib.Observation(
                        observingmode=obs.get("processSubtype"),
                        instrumentfilter=obs.get("bandFilter")[4:].replace("_","-") +" MHz",
                        clock_frequency=int(obs.get("sampleClock")), #obs.get("clockMode")[-3:]
                        clock_frequencyunit=constants.FREQUENCYUNIT_MHZ,
                        stationselection=constants.STATIONSELECTIONTYPE_CORE, # todo
                        antennaset=antennaset,
                        timesystem=constants.TIMESYSTEMTYPE_UTC, # todo
                        stations=stations,
                        numberofstations=len(stations),
                        numberofsubarraypointings=len(pointings),
                        numberoftbbevents=len(tbbevents),
                        numberofcorrelateddataproducts=dps.get("nrOfOutput_Correlated_"),
                        numberofbeamformeddataproducts=dps.get("nrOfOutput_Beamformed_"),
                        numberofbitspersample=5, # todo
                        process_map=siplib.ProcessMap(
                            strategyname=obs.get("strategy"),
                            strategydescription="awesome strategy",  # todo
                            starttime=obs.get("startTime").replace(" ","T"),
                            duration= duration,
                            identifier=siplib.Identifier(source="test"), # todo: Not possible to obtain the ID that this has in the catalog based on the feedback?
                            observation_identifier=siplib.Identifier(source="test"), #obs.get(some_beam).get("momID"), # todo: Not possible to obtain the ID that this has in the catalog based on the feedback?
                            #parset_source="parsource", # todo
                            #parset_id="parid", #todo,
                            relations=[siplib.ProcessRelation(
                                identifier=siplib.Identifier(source="test") #todo: Not possible to obtain this?
                                )],
                        ),
                        observationdescription=campaign.get("title"), #todo
                        #channelwidth_frequency=160, #todo
                        #channelwidth_frequencyunit="MHz", #todo
                        #channelspersubband=5,#todo
                        subarraypointings=pointings,
                        transientbufferboardevents=tbbevents,
                    )
                )
                sips[filename] = sip
            except Exception as err:
                if not filename:
                    filename = "UNDEFINED"
                print("Could not create SIP for", filename,"->",err)

        if sips:
            return sips
        else:
            return None


def example(fil):
    print("Now running example on file", fil)

    with open(fil) as f:
        text = f.readlines()
        feedback = Feedback(text)

        # A) Parse complete SIP:
        sips = feedback.get_dataproduct_sips(obs_prefix="ObsSW.Observation", dp_prefix="Observation.DataProducts")
        for key in list(sips.keys()):
            print("Created SIP for file "+ str(key))


        # B) Alternatively: Parse dataproducts from pseudo-feedback (specialty of Leiden group):

        process_identifier = siplib.Identifier(source='test') # create process identifier
        sapointing_identifier = siplib.Identifier(source='test') # create subarra ypointing identifier

        # either provide identifiers as args...
        dataproducts = feedback.get_dataproducts(process_identifier=process_identifier, subarraypointing_identifier=sapointing_identifier, prefix="test.prefix" )

        # ...or set them explicitely
        for dp in dataproducts:
            dp.set_identifier(siplib.Identifier('test')) # create new unique ID for dataproduct
            dp.set_process_identifier(process_identifier) # set the identifier of the creating process
            dp.set_subarraypointing_identifier(sapointing_identifier) # assign the pointing identifier

        # Create example doc:
        sip = siplib.Sip(
            project_code="code",
            project_primaryinvestigator="pi",
            project_contactauthor="coauthor",
            #project_telescope="LOFAR",
            project_description="awesome project",
            project_coinvestigators=["sidekick1", "sidekick2"],
            dataproduct=dataproducts[0] # output dp (using input one here for testing)
        )

        for dp in dataproducts:
            sip.add_related_dataproduct(dp) # input dps


        sip.prettyprint()



def main(argv):

    print("! This is a stub, the feedback to SIP conversion is not correctly working at this point.")
    print("! You may use this as a module to do some feedback parsing, but unfortunately not all information can be determined from feedback to create a valid SIP.")

    if argv[1] is not None:
        example(argv[1])


if __name__ == '__main__':
    main(sys.argv)

