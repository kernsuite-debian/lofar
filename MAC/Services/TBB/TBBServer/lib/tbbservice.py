#!/usr/bin/env python3

# Copyright (C) 2015
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from socket import gethostname
from optparse import OptionParser
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
from time import sleep

import logging
logger = logging.getLogger()

from lofar.messaging import RPCService, DEFAULT_BROKER, DEFAULT_BUSNAME, ServiceMessageHandler
from lofar.messaging.messages import EventMessage
from lofar.messaging.messagebus import ToBus
from lofar.common.util import waitForInterrupt
from lofar.mac.tbbservice.config import *
from lofar.common.lcu_utils import *
from lofar.common.cep4_utils import *
from lofar.common.subprocess_utils import communicate_returning_strings
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.mac.tbb.tbb_load_firmware import load_tbb_firmware
from lofar.mac.tbb.tbb_freeze import freeze_tbb
from lofar.mac.tbb.tbb_release_recording import release_tbb
from lofar.mac.tbb.tbb_restart_recording import restart_tbb_recording
from lofar.mac.tbb.tbb_set_storage import set_tbb_storage, create_mapping
from lofar.mac.tbb.tbb_start_recording import start_tbb
from lofar.mac.tbb.tbb_upload_to_cep import upload_tbb_data
from lofar.parameterset import parameterset
from lofar.mac.tbb.tbb_util import parse_parset_from_voevent, get_cpu_nodes_available_for_tbb_datawriters_sorted_by_load
from lofar.common.lcu_utils import stationname2hostname
from lofar.mac.tbb.tbb_caltables import add_station_calibration_tables_h5_files_in_directory
from lofar.mac.tbb.tbb_cable_delays import add_dipole_cable_delays_h5_files_in_directory
from lofar.mac.tbbservice.server.tbbservice_config import *
from lofar.common.util import single_line_with_single_spaces

class TBBServiceMessageHandler(ServiceMessageHandler):

    def __init__(self):
        super().__init__()

        # Keep the running datawriter process information in this dict.
        self.procs = {}

    def _send_event_message(self, subject, content):
        prefixed_subject = '%s.%s' % (DEFAULT_TBB_NOTIFICATION_PREFIX, subject)
        logger.info('Sending notification to %s with subject \'%s\' %s' % (self.exchange,
                                                                           prefixed_subject,
                                                                           single_line_with_single_spaces(str(content))))
        self.send(EventMessage(subject=prefixed_subject,
                               content=content))

    def _update_parset(self, parset, updates):
        """
        Update the values in the parset with the values of the updates dict.
        All parset keys that contain the update key are updated, so this matches irrespective of prefixes.
        If no existing entry is found, the update key and value are added to the parset.
        :param parset: The parameterset object to update
        :param updates: A dict with the updates
        :return: The updated parameterset object
        """
        # Note: this could be a simple dict update, if we don't have to check for substrings.
        #       But I assume this is required to allow prefixes or sth like that.
        # Note: ICD states that non-filled-in parameters should/can be present, and should contain 0 by default.

        if isinstance(parset, parameterset):
            parset = parset.dict()

        if isinstance(updates, parameterset):
            updates = updates.dict()

        for dk, dv in list(updates.items()):
            found_in_parset = False
            for k, v in list(parset.items()):
                if dk in k:
                    found_in_parset = True
                    #parset.replace(k, dv) <- does not work with parameterset during live testing for some reason
                    parset[k] = dv
            if not found_in_parset:
                # parset.add(dk, dv)
                parset[dk] = dv

        return parameterset(parset)

    def _get_parset_of_running_obs(self):
        """
        determine running observation from RA, then query its parset from OTDB.
        :return: the parset of the running obs
        """

        logger.info("determining running observation...")

        # fetch parset of current active observation and save a modified version for the tbb writers
        with RADBRPC.create(exchange=self.exchange, broker=self.broker) as rarpc:
            running_observations = rarpc.getTasks(task_status='active', task_type='observation')

            if not running_observations:
                raise RuntimeError("No active observation found. Cannot create parset for TBB writer.")

            # pick first TODO: determine actual relevant observation
            otdb_id = running_observations[0]['otdb_id']

            logger.info("running observation otdb_id=%s. Fetching parset...", otdb_id)

            with OTDBRPC.create(exchange=self.exchange, broker=self.broker) as otdbrpc:
                return parameterset(otdbrpc.taskGetSpecification(otdb_id=otdb_id)['specification'])

    def prepare_alert_tbb_parset(self, voevent=""):
        """
        Create a parset from running obs and voevent xml, write to file
        :return: tuple of the parset file and the parset itself
        """

        # TODO, replace with actual path
        parset_path = '/data/scratch/tbb_alert_%s.parset' % datetime.utcnow().strftime("%Y%m%d%H%M%S")

        # get base parset from otdb
        parset = self._get_parset_of_running_obs()

        # sanity check
        if 'HBA' not in parset.getString('ObsSW.Observation.antennaArray'):
            raise RuntimeError('Current antennaArray is %s. Not starting TBB datawriters.' % (
                                parset.get('ObsSW.Observation.antennaArray'),))

        # update parset with TBB subband mode keys and default values
        defaults_parset = {
            'Observation.TBB.TBBsetting.operatingMode': '2',
            'Observation.TBB.TBBsetting.subbandList': '[10..489]',
            'Observation.TBB.TBBsetting.triggerDispersionMeasure': 0,
            'Observation.TBB.TBBsetting.triggerDispersionMeasureUnit': "pc cm^-3",
            'Observation.TBB.TBBsetting.time': 0,  # -> time.time() ???
            'Observation.TBB.TBBsetting.sampleNumber': 0,
            'Observation.TBB.TBBsetting.fitDirectionCoordinateSystem': 0,
            'Observation.TBB.TBBsetting.fitDirectionAngle1': 0,
            'Observation.TBB.TBBsetting.fitDirectionAngle2': 0,
            'Observation.TBB.TBBsetting.fitDirectionDistance': 0,
            'Observation.TBB.TBBsetting.fitDirectionVariance': 0,
            'Observation.TBB.TBBsetting.referenceFrequency': 0,
            'Observation.TBB.TBBsetting.observatoryCoordinates': 0,
            'Observation.TBB.TBBsetting.observatoryCoordinatesCoordinateSystem': 0,
            'Observation.TBB.TBBsetting.triggerId': 0,
            #'Observation.TBB.TBBsetting.additionalInfo': voevent,
            # older keys we probably still want to fill here:
            'Observation.TBB.TBBsetting.triggerType': 'Unknown',
            'Observation.TBB.TBBsetting.triggerVersion': 0
        }
        parset = self._update_parset(parset, defaults_parset)

        # update parset with values from received voevent
        try:
            voevent_parset = parse_parset_from_voevent(voevent)
            parset = self._update_parset(parset, voevent_parset)
        except Exception as e:
            logger.warning("prepare_alert_tbb_parset: error '%s' while parsing voevent %s", e, voevent)

        return parset_path, parset

    def start_datawriters(self, output_path, num_samples_per_subband, voevent=""):
        """
        start the tbb datawriters and notify when done.
        :param output_path: string defining the full directory path where to save the data, like: "/data/projects/<my_project>/L<obs_id>/
        :param num_samples_per_subband: integer value for number of samples to expect (depending on duration, 1 sample = 5.12 microseconds)
        :param voevent: voevent xml string (for metadata)
        :return: nodes where a datawriter has been started as list of strings
        """
        self._send_event_message('DataWritersStarting', {})

        parset_path, parset = self.prepare_alert_tbb_parset(voevent)

        # this is a list of ports for the dutch stations only
        # TODO: make dynamic, depending on which stations are actually used
        ports = ','.join(str(x) for x in range(31664, 31670))

        # TODO: do not start more dw's than there are stations.
        available_nodes = get_cpu_nodes_available_for_tbb_datawriters_sorted_by_load(min_nr_of_free_nodes=5)

        start = datetime.utcnow()
        timeout = timedelta(days=1) #TODO: make timeout configurable (or an argument)

        #create output dir
        cmd = ['mkdir', '-p', output_path]
        cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)
        logger.info('creating output dir on cep4: %s, executing: %s', output_path, ' '.join(cmd))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = communicate_returning_strings(proc)

        if proc.returncode != 0:
            raise RuntimeError("Error while creating output dir '%s': %s" % (output_path, out+err))

        #write parset
        parset_dict = parset.dict()
        parset_str = '\n'.join('%s = %s' % (k,parset_dict[k]) for k in sorted(parset_dict.keys())).replace('"', '').replace('ObsSW.', '')
        cmd = ['echo', '\"%s\"' % (parset_str,), '>', parset_path]
        cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)
        logger.info('writing tbb datawriter parset, executing: %s', ' '.join(cmd))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = communicate_returning_strings(proc)

        if proc.returncode != 0:
            raise RuntimeError("Error while writing parset: %s" % (out+err, ))

        # TODO: what should be do if datawriters are already running? kill/wait for them first?
        self.procs = {}

        for node in available_nodes:
            cmd = ['TBB_Writer',
                   '-s', parset_path,
                   '-p', ports,
                   '-k', '0',
                   '-t', '60',
                   '-d', str(num_samples_per_subband),
                   '-o', output_path]

            # wrap the command in a cep4 docker ssh call
            cmd = wrap_command_for_docker(cmd, DATAWRITER_DOCKER_IMAGE_NAME, DATAWRITER_DOCKER_IMAGE_TAG,
                                          mount_dirs=['/data/projects', '/data/scratch', '/data/share', '/data/parsets'],
                                          added_privileges=True)
            cmd = wrap_command_in_cep4_cpu_node_ssh_call(cmd, node, via_head=True)

            logger.info('starting datawriter on node %s, executing: %s', node, ' '.join(cmd))

            proc = Popen(cmd)
            self.procs[node] = proc

        self._send_event_message('DataWritersStarted', {})
        return list(self.procs.keys())

    def wait_for_datawriters(self, timeout = 24 * 3600):
        '''
        Monitor started procs until they are all done or timeout seconds have
        passed.
        :param timeout:  Timeout in seconds until data writers will be
        forcefully killed.  The default is 24 hours.
        '''
        start = datetime.utcnow()
        while self.procs:
            logger.info('waiting for %d datawriters to finish...', len(self.procs))

            finished_procs = { node: proc for node, proc in list(self.procs.items())
                               if proc.poll() is not None}

            if finished_procs:
                for node, proc in list(finished_procs.items()):
                    logger.info('datawriter on node %s finished with exitcode=%d', node, proc.returncode)
                    del self.procs[node]
            else:
                sleep(1.0)

            if datetime.utcnow() - start >= timeout:
                logger.warning('timeout while waiting for %d more datawriters...', len(self.procs))
                self.stop_datawriters()
        self._send_event_message('DataWritersFinished', {})

    def stop_datawriters(self):
        '''Stop TBB datawriters running on CEP4 and notify when done'''
        self._send_event_message('DataWritersStopping', {})
        for node, proc in list(self.procs.items()):
            logger.warning('killing datawriter on node: %s', node)
            proc.kill()
            del self.procs[node]
        self._send_event_message('DataWritersStopped', {})

        # also call 'normal' wait_for_datawriters method,
        # which has no datawriter to wait for anymore...
        # but as a result, it sends a 'DataWritersFinished' event.
        self.wait_for_datawriters()
        # TODO: fire off a docker image as described in SW-552

    def get_station_calibration_tables(self, stations):
        """
        Retreive the calibration tables from the given list (or comma-seperated string) of stations.
        :param stations:  string - single station in string, or multiple stations in csv-string, or multiple station in list of strings. Only TBBs of these stations will be commanded to start data recording.
        :return: dict - dictionary of stationname->caltable
        """
        # TODO: Is this method needed here in the service? Probably not. Remove it if obsolete after SW-552.

        if isinstance(stations, str):
            stations = [s.strip() for s in stations.split(',')]

        # determine antenna_set_and_filter for the proper caltables from the current observation's parset.
        # TODO: maybe antenna_set_and_filter should be a parameter and the parset parsing should be done in the calling method (from the master recipe for example)
        parset = self._get_parset_of_running_obs()
        antennaSet = parset.getString('ObsSW.Observation.antennaSet') # like: LBA_OUTER
        if antennaSet.startswith('HBA'):
            antennaSet = 'HBA' #HBA caltables do not make distinction between different HBA sets
        bandFilter = parset.getString('ObsSW.Observation.bandFilter') # like: LBA_10_90
        antenna_set_and_filter = '%s-%s' %( antennaSet, bandFilter[4:]) # yields result like: LBA_OUTER-10_90

        return get_station_calibration_tables(stations, antenna_set_and_filter)

    def switch_firmware(self, stations, mode):
        """
        Command TBBs to switch to one of two firmwares:  sub-band mode or raw voltage mode.
        :param stations:  string - Only TBBs of these stations will be commanded to start data recording.
        :param mode:  string - Parameter to set-up data recording in either \"subband\" or \"rawvoltage\" mode.
        """
        log_message = "Switching TBB firmware on stations %s to \"%s\"" % (stations, mode)
        logger.info(log_message + "...")
        load_tbb_firmware(stations, mode)
        logger.info(log_message + " done.")

    def start_recording(self, stations, mode, subbands):
        """
        Command TBBs in ALERT mode to start data recording.
        :param stations:  string - Only TBBs of these stations will be commanded to start data recording.
        :param mode:  string - Parameter to set-up data recording in either \"subband\" or \"rawvoltage\" mode.
        :param sub_bands:  string - The list of sub-bands that the RSP will be set-up for.
        """
        log_message = "Starting the TBB data recording for mode %s on stations %s in sub-bands %s" % (mode, stations, subbands)
        logger.info(log_message + "...")
        start_tbb(stations, mode, subbands)
        logger.info(log_message + " done.")

    def freeze_data(self, stations, dm, timesec, timensec):
        """
        Command TBBs in ALERT mode to freeze the contents of their memory.  This stops recording but does not discard the already recorded data.
        :param stations:  string - Only TBBs of these stations will freeze their memory contents.
        :param dm:  float - The dispersion measure that is to be set in the TBBs.
        :param timesec:  int- The start time of the data recording in seconds since 1970-01-01T00.00.00.  This is the integer part of the seconds.
        :param timensec:  int - The start time of the data recording in seconds since 1970-01-01T00.00.00.  This is the fractional part as integer in nanoseconds.
        """
        log_message = "Freezing the TBB data on stations %s.  DM = %s, time = %f" % (stations, dm, (float(timesec) + (1e-9 * int(timensec))))
        logger.info(log_message + "...")
        freeze_tbb(stations, dm, timesec, timensec)
        logger.info(log_message + " done.")

    # todo: treat start_time as sec, nsec tuple instead of float for higher precision
    def upload_data(self, stations, dm, start_time, duration, sub_bands, wait_time, boards):
        """
        Command TBBs in ALERT mode to upload part or all of their memory to CEP.
        :param stations:  string - Only TBBs of these stations will upload their data to CEP.
        :param dm:  float - The dispersion measure that was set during data recording.
        :param start_time:  float - Designates the start of the recorded data in the TBB memory which will be uploaded to CEP.  Earlier data in TBB memory will not be uploaded.  0.0s is 1970-01-01T00.00.00.
        :param duration:  float - The time span for which the data will be uploaded.
        :param sub_bands:  string - The list of sub-bands that will be uploaded.
        :param wait_time:  float - The time that has to be waited before another sub-band upload can be commanded.
        :param boards:  string - Only these boards will be commanded to upload the spectral data to CEP.
        """
        log_message = "Uploading the TBB data on stations %s, " \
                      "boards = %s, " \
                      "sub-bands = %s, " \
                      "dm = %f, " \
                      "start_time = %f, " \
                      "duration = %f, " \
                      "wait time = %f" % (stations, boards, sub_bands, dm, start_time, duration, wait_time)
        logger.info(log_message + "...")
        upload_tbb_data(stations, dm, start_time, duration, sub_bands, wait_time, boards)
        logger.info(log_message + " done.")

    def _add_meta_data_to_h5_files(self, h5_dir):
        """
        Scan the tbb h5 files in the given h5_dir, and add all known meta-data to the files.
        :param h5_dir: path to dir containing one or more tbb h5 files
        """
        add_station_calibration_tables_h5_files_in_directory(h5_dir)
        add_dipole_cable_delays_h5_files_in_directory(h5_dir)
        #TODO: add more metadata. To be implemented in e.g. SW-561

    def release_data(self, stations):
        """
        Command TBBs in ALERT mode to release data recording.
        :param stations:  string - Only TBBs of these stations will be commanded to stop data recording.
        """
        log_message = "Releasing the TBB data recording on stations %s" % (stations)
        logger.info(log_message + "...")
        release_tbb(stations)
        logger.info(log_message + " done.")

    def restart_recording(self, stations):
        """
        Command TBBs in ALERT mode to re-start data recording. This preserves the original mode and subband settings.
        :param stations:  string - Only TBBs of these stations will be commanded to re-start data recording.
        """
        log_message = "Restarting the TBB data recording on stations %s" % (stations)
        logger.info(log_message + "...")
        restart_tbb_recording(stations)
        logger.info(log_message + " done.")

    def set_storage(self, map):
        """
        Command TBBs in ALERT mode to stream data to specific CEP nodes.
        :param map: dict - containing a one on one mapping of station LCUs to nodes
        """
        log_message = "Setting the storage nodes where TBB data is received to: %s" % (map)
        logger.info(log_message + "...")
        set_tbb_storage(map)
        logger.info(log_message + " done.")

    def do_tbb_subband_dump(self, starttime, duration, dm, project, triggerid,
                            stations, subbands, boards, nodes, voevent_xml,
                            stoptime=None, rcus=None):
        """
        This 'recipe' call performs all the needed steps to do a tbbdump on tbb boards with already frozen data.
        The first data of the dump is recorded at starttime in the subband of highest frequency. Subbands of lower frequency
        are then delayed by an offset calculated from the provided dm, and each subband holds data of the provided duration.
        Hence, the starttime should predate the expected time of arrival of the event at the frequency of the highest
        subband by half the recording duration to center the event in the recorded data for all subbands.

        :param starttime: The starttime of the recording
        :param duration: The duration of the recording in seconds as float
        :param dm: The dispersion measure (in pc/cm^3) of the event to capture as float
        :param project: The project identifier as string
        :param triggerid: The trigger identifier as string
        :param stoptime: The stoptime in seconds since Epoch as float
        :param stations: The stations to use as list of strings
        :param subbands: The subbands to use as list of integers
        :param rcus: The receivers to use as list of integers
        :param boards: The tbb boards to use as list of integers
        :param nodes: The CEP nodes to send data to
        :param voevent_xml: the entire voevent in xml as string
        :return:
        """

        log_message = "Performing TBB data dump to CEP for trigger %s and project %s " % (triggerid, project)
        logger.info(log_message + "...")

        # todo
        if rcus is not None:
            logger.warning("rcus option is not implemented. Ignoring that one.")
        if stoptime is not None:
            logger.warning(
                "stoptime option is not implemented. Ignoring that one.")  # todo: remove kwarg or make duration optional?

        # convert station list to list of lcus, as the tbb service requires it
        lcus = [stationname2hostname(station) for station in stations]
        lcus_str = ",".join(lcus)

        # convert float starttime to second and nanosecond component
        # todo: Do we need higher precision up to here? Investigate!
        #    ...We agreed to try this out first, but it could be problematic fr use cases with extremely short recordings.
        sec, nsec = ("%.9f" % starttime).split(".")
        sec = int(sec)
        nsec = int(nsec)

        # determine time to wait between dump of individual subbands
        waittime = DEFAULT_CONSTANT_TIME_BETWEEN_SUBBAND_DUMPS + \
                   DEFAULT_DURATION_FACTOR_BETWEEN_SUBBAND_DUMPS * float(duration)

        # TODO: replace triggerid by running tbb-observation's otdb_id?
        sanitized_triggerid = triggerid.replace('/', '_').replace(':', '_').replace('#', '_')
        output_path = '/data/projects/%s/tbb_spectral/%s' % (project, sanitized_triggerid)

        # determine number of samples
        num_samples = int(float(duration) // 0.00000512)

        datawriter_nodes = self.start_datawriters(output_path=output_path, num_samples_per_subband=num_samples, voevent=voevent_xml)
        if nodes is None:
            logger.info('Nodes to use are not configured, using all with datawriter')
            nodes = ['cpu%02d' % (node,) for node in datawriter_nodes]
        else:
            logger.info('Filtering node list for those who actually have a running datawriter')
            nodes = ['cpu%02d' % (node,) for node in nodes if node in datawriter_nodes]

        # create mapping for storage nodes
        try:
            storage_map = create_mapping(lcus, nodes)
            self.set_storage(storage_map)
        except:
            logger.exception('Could not create storage map. Will try to dump anyway.')

        # start upload
        try:
            self.upload_data(lcus_str, dm, starttime, duration, subbands, waittime, boards)
        except:
            logger.exception('Error while uploading tbb data to cep.')

        try:
            self._add_meta_data_to_h5_files(output_path)
        except:
            logger.exception('Error adding meta-data to h5 files in %s.' % (output_path,))

        # restart recording
        self.restart_recording(lcus_str)
        logger.info(log_message + " done.")


def main():
    '''main method which starts the TBBControlService with the cmdline supplied options and then waits until stopped by an interrupt.'''
    # make sure we run in UTC timezone
    os.environ['TZ'] = 'UTC'

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='run the tbb service, which can be used to e.g. start the datawriters, start/stop tbb recordings, or start streaming to CEP.')
    parser.add_option('-q', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')

    parser.add_option("-b", "--busname", dest="busname", type="string",
                      default=DEFAULT_BUSNAME,
                      help="Name of the bus on which the tbb service listens and tbb notifications are published. [default: %default]")
    (options, args) = parser.parse_args()

    with RPCService(service_name=DEFAULT_TBB_SERVICENAME,
                    handler_type=TBBServiceMessageHandler,
                    exchange=options.busname,
                    broker=options.broker,
                    num_threads=1):

        logger.info('*****************************************')
        logger.info('Started TBBService')
        logger.info('*****************************************')

        waitForInterrupt()

if __name__ == '__main__':
    main()

