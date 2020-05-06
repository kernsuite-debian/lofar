from lofar.lta.sip import siplib
from lofar.lta.sip import query
from lofar.lta.sip import visualizer
import uuid

input_project = '2015LOFAROBS'
input_obsid = '1566501'

output_dataproduct_name = 'random_10M_001'

# query ids of output dataproducts of given obs
input_dpids = query.get_dataproduct_ids(input_project, input_obsid)

# query sips for each dataproduct id
input_sips = []
for input_dpid in input_dpids:
   xml = query.get_dataproduct_sip(input_project, input_dpid)
   dpsip = siplib.Sip.from_xml(xml)
   input_sips.append(dpsip)

# obtain important metadata required for SIP creation form the input SIPs:
indpids = [x.get_dataproduct_identifier() for x in input_sips] # we have the ids as string already, but we obtain the actual identifier objects here
sapid = input_sips[0].get_dataproduct_subarraypointing_identifier() # determine the SAP identifier. Note: This may or may not stay the same depending on what you did to the data!

# create identifier, can be looked up later
pipelabel = 'myprocesslabel_'+str(uuid.uuid4())
dplabel = 'mydataproductlabel_'+str(uuid.uuid4())
siplib.Identifier('test', userlabel=pipelabel)
siplib.Identifier('test', userlabel=dplabel)

mysip = siplib.Sip(
            project_code=input_project,
            project_primaryinvestigator="pi",
            project_contactauthor="coauthor",
            #project_telescope="LOFAR",
            project_description="awesome project",
            project_coinvestigators=["sidekick1", "sidekick2"],
            dataproduct=siplib.CorrelatedDataProduct(
                siplib.DataProductMap(
                    type="Unknown",
                    identifier=siplib.Identifier.lookup('test', userlabel=dplabel),
                    size=1024,
                    filename=output_dataproduct_name,
                    fileformat="HDF5",
                    process_identifier=siplib.Identifier.lookup('test',  userlabel=pipelabel)
                ),
                subarraypointing_identifier=sapid,
                subband="1",
                starttime="2017-03-23T10:20:15",
                duration= "PT1H",
                integrationinterval=10,
                integrationintervalunit="ms",
                central_frequency=160,
                central_frequencyunit="MHz",
                channelwidth_frequency=200,
                channelwidth_frequencyunit="MHz",
                channelspersubband=122,
            )
        )

mysip.add_pipelinerun(
            siplib.CalibrationPipeline(
                siplib.PipelineMap(
                    name="virtualcalpipeline",
                    version="0.9",
                    sourcedata_identifiers=indpids,
                    process_map=siplib.ProcessMap(
                        strategyname="strategy1",
                        strategydescription="awesome strategy",
                        starttime="1980-03-23T10:20:15",
                        duration= "PT5H",
                        identifier=siplib.Identifier.lookup('test', userlabel=pipelabel),
                        observation_identifier=siplib.Identifier.lookup('test', userlabel=pipelabel), #  despite the confusing naming: same as identifier (in case of user ingest)
                        relations=[]
                    )),
                skymodeldatabase="db",
                numberofinstrumentmodels=1,
                numberofcorrelateddataproducts=1,
            )
        )

for input_sip in input_sips:
    mysip.add_related_dataproduct_with_history(input_sip)

mysip.save_to_file(output_dataproduct_name+'_sip.xml')

visualizer.visualize_sip(mysip, path=output_dataproduct_name+"_visualization")
