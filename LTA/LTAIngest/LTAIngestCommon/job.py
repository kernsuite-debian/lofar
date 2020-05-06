import os, os.path
import logging
logger = logging.getLogger()

#JobState: Below are hardcoded defines for communicating with MoM!
JobFailed    = -1
JobHold      =  0
JobScheduled =  1
JobProducing =  2
JobProduced  =  3

#JobState: Only internal in the Ingest
JobToDo           = 10
JobRetry          = 11
JobRemoved        = 12
JobTransferFailed = 13

def jobState2String(jobstate):
    if jobstate == JobToDo:
        return "%d (JobToDo)" % jobstate
    if jobstate == JobRetry:
        return "%d (JobRetry)" % jobstate
    if jobstate == JobFailed:
        return "%d (JobFailed)" % jobstate
    if jobstate == JobHold:
        return "%d (JobHold)" % jobstate
    if jobstate == JobScheduled:
        return "%d (JobScheduled)" % jobstate
    if jobstate == JobProducing:
        return "%d (JobProducing)" % jobstate
    if jobstate == JobProduced:
        return "%d (JobProduced)" % jobstate
    if jobstate == JobRemoved:
        return "%d (JobRemoved)" % jobstate
    if jobstate == JobTransferFailed:
        return "%d (JobTransferFailed)" % jobstate
    return str(jobstate)

#file data types
FILE_TYPE_CORRELATED   = 0
FILE_TYPE_BEAMFORMED   = 1
FILE_TYPE_IMAGE        = 2
FILE_TYPE_UNSPECIFIED  = 3
FILE_TYPE_PULP         = 4

def parseJobXmlFile(job_xml_path):
    with open(job_xml_path, 'r') as file:
        return parseJobXml(file.read())

def parseJobXml(job_xml):
    logger.debug('parseJobXml: %s', job_xml.replace('\n', ' '))
    job_dict = {}
    try:
        from xml.dom import minidom, Node
        doc = minidom.parseString(job_xml)
        if doc.documentElement.nodeName == 'exportjob':
            job_dict['ExportID'] = str(doc.documentElement.attributes.get('exportID').nodeValue)
            for node in doc.documentElement.childNodes:
                if node.nodeName == 'inputlist':
                    name  = "'" + node.attributes.get('name').nodeValue + "'"
                    exec(eval("'job_dict[%s] = []' % (name)"))
                    for itemnode in node.childNodes:
                        if itemnode.nodeName == 'listitem':
                            value = itemnode.childNodes[0].nodeValue
                            exec(eval("'job_dict[%s].append(%s)' % (name, value)"))
                elif node.nodeName == 'input':
                    name  = "'" + node.attributes.get('name').nodeValue + "'"
                    value = node.childNodes[0].nodeValue
                    if value == 'True' or value == 'False':
                        exec(eval("'job_dict[%s] = %s' % (name, value)"))
                    else:
                        value = "'''" + value + "'''" ## tripple quotes because a value could be "8 O'clock" for example
                        exec(eval("'job_dict[%s] = %s' % (name, value)"))

        if job_dict['ExportID']: ## we need an export ID to identify the job
            if job_dict['ObservationId'][0] == 'L':
                job_dict['ObservationId'] = job_dict['ObservationId'][1:]
            test = int(job_dict['ObservationId']) ## check if it can be converted to an int
            test = int(job_dict['ArchiveId']) ## check if it can be converted to an int
            if not "Type" in job_dict:
                job_dict["Type"] = "MoM"

            if not "JobId" in job_dict:
                job_dict["JobId"] = job_dict['ExportID']

            #try to extract a job_group_id
            job_dict['job_group_id'] = 'unknown_group'
            if 'ExportID' in job_dict:
                try:
                    job_dict['job_group_id'] = int(job_dict['ExportID'].split('_')[1])
                except:
                    pass
            if 'IngestGroupId' in job_dict:
                job_dict['job_group_id'] = job_dict['IngestGroupId']

            if not "priority" in job_dict:
                job_dict['priority'] = 4 #default 'normal' priority on scale of 0 (lowest) to 9 (highest)
            else:
                try:
                    job_dict['priority'] = int(job_dict['priority'])
                except ValueError:
                    job_dict['priority'] = 4 #default 'normal' priority on scale of 0 (lowest) to 9 (highest)

            job_dict['file_type'] = FILE_TYPE_UNSPECIFIED

            if any([extention.lower() in job_dict['DataProduct'].lower() for extention in ['sky', 'FITS']]): #Not for FITS and HDF5 Images
                job_dict['FileName'] = job_dict['DataProduct']
                job_dict['file_type'] = FILE_TYPE_IMAGE
            elif '.tar' in job_dict['DataProduct'].lower():
                job_dict['FileName'] = job_dict['DataProduct']
            else:
                job_dict['FileName'] = job_dict['DataProduct'] + '.tar'

            #determine file_type from DataProduct name
            #if DataProduct name is conform lofar standards, this is safe to do
            if 'uv' in job_dict['DataProduct']:
                job_dict['file_type'] = FILE_TYPE_CORRELATED
            if 'bf' in job_dict['DataProduct']:
                if 'h5' in job_dict['DataProduct']:
                    job_dict['file_type'] = FILE_TYPE_BEAMFORMED
                else:
                    job_dict['file_type'] = FILE_TYPE_PULP
            if 'summary' in job_dict['DataProduct']:
                job_dict['file_type'] = FILE_TYPE_PULP

            return job_dict
    except Exception as e:
        if logger:
            logger.exception('Failed importing job: %s\n%s', job_xml, e)
        job_dict['Status'] = JobFailed
    return job_dict

def updatePriorityInJobFile(job_file_path, priority):
    try:
        from xml.dom import minidom, Node
        priority = max(0, min(9, int(priority)))

        with open(job_file_path, 'r') as file:
            contents = file.read()

        doc = minidom.parseString(contents)
        if doc.documentElement.nodeName == 'exportjob':
            input_nodes = [cn for cn in doc.documentElement.childNodes if cn.nodeName == 'input']
            priority_input_nodes = [n for n in input_nodes if n.attributes.get('name').nodeValue == 'priority']
            if priority_input_nodes:
                for pn in priority_input_nodes:
                    pn.childNodes[0].nodeValue = priority
            else:
                pin = doc.createElement('input')
                pin.setAttribute('name', 'priority')
                pin.appendChild(doc.createTextNode(str(priority)))
                doc.documentElement.appendChild(pin)

        with open(job_file_path, 'w') as file:
            file.write(doc.toprettyxml())
    except Exception as e:
        logger.error(e)

def createJobXmlFile(path, project_name, mom_export_id, obs_id, dataproduct_name, archive_id, location, submitter=None, description=None, priority=4):
    dirname = os.path.dirname(path)
    #create dir dir if not exists
    if not os.path.isdir(dirname):
        try:
            os.makedirs(dirname)
        except OSError as e:
            logger.error(e)

    with open(path, 'w') as file:
        file.write(createJobXml(project_name, mom_export_id, obs_id, dataproduct_name, archive_id, location, submitter, description, priority))

def createJobXml(project_name, mom_export_id, obs_id, dataproduct_name, archive_id, location, submitter=None, description=None, priority=4):
    job_id = 'A_%s_%s_%s' % (mom_export_id, archive_id, dataproduct_name)
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<exportjob exportID="{job_id}">
    <input name="DataProduct">{dataproduct_name}</input>
    <input name="Project">{project_name}</input>
    <input name="JobId">{job_id}</input>
    <input name="ArchiveId">{archive_id}</input>
    <input name="ObservationId">{obs_id}</input>
    <input name="Location">{location}</input>
    <input name="Mom2Id">{mom_export_id}</input>'''.format(job_id=job_id,
                                                           dataproduct_name=dataproduct_name,
                                                           project_name=project_name,
                                                           archive_id=archive_id,
                                                           obs_id=obs_id,
                                                           location=location,
                                                           mom_export_id=mom_export_id)

    if submitter:
        xml += '\n    <input name="Submitter">%s</input>' % submitter

    if description:
        xml += '\n    <input name="Description">%s</input>' % description

    if priority:
        xml += '\n    <input name="priority">%s</input>' % priority

    xml += '\n</exportjob>'
    return xml
