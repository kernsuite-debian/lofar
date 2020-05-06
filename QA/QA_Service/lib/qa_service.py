# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

# $Id: qa_service.py 43930 2019-08-30 07:57:17Z klazema $

import os.path
import logging
from subprocess import call, Popen, PIPE, STDOUT
from optparse import OptionParser, OptionGroup
from threading import Thread
from lofar.common.util import waitForInterrupt
from lofar.sas.otdb.OTDBBusListener import OTDBBusListener, OTDBEventMessageHandler, DEFAULT_OTDB_NOTIFICATION_SUBJECT
from lofar.messaging import UsingToBusMixin, BusListener
from lofar.messaging.messages import EventMessage
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.qa.service.config import DEFAULT_QA_NOTIFICATION_SUBJECT_PREFIX
from lofar.common.cep4_utils import *
from lofar.parameterset import parameterset
from lofar.sas.otdb.otdbrpc import OTDBRPC

logger = logging.getLogger(__name__)

QA_LUSTRE_BASE_DIR = '/data/qa'
QA_NFS_BASE_DIR = '/qa'
DEFAULT_FILTERED_OTDB_NOTIFICATION_SUBJECT = "filtered.%s" % (DEFAULT_OTDB_NOTIFICATION_SUBJECT,)

#TODO:  idea: convert periodically while observing?

class QAFilteringOTDBBusListener(OTDBBusListener):
    class QAFilteringOTDBEventMessageHandler(UsingToBusMixin, OTDBEventMessageHandler):
        def _send_filtered_event_message(self, otdb_id: int, modificationTime: datetime, state: str):
            try:
                with OTDBRPC.create(exchange=self.exchange, broker=self.broker, timeout=2) as otdbrpc:
                    parset = parameterset(otdbrpc.taskGetSpecification(otdb_id=otdb_id).get("specification", ''))
                    task_type = parset.get("ObsSW.Observation.processType")
                    priority = 6 if task_type == "Observation" else 2
            except Exception as e:
                logger.warning('Could not determine task type for otdb_id=%s, using default priority=4: %s', otdb_id, e)
                priority = 4

            try:
                content = {"treeID": otdb_id,
                           "state": state,
                           "time_of_change": modificationTime}
                msg = EventMessage(subject=DEFAULT_FILTERED_OTDB_NOTIFICATION_SUBJECT,
                                   content=content,
                                   priority=priority)
                logger.info('sending filtered event message subject:\'%s\' content: %s', msg.subject, content)
                self.send(msg)
            except Exception as e:
                logger.error('Could not send event message: %s', e)

        def onObservationCompleting(self, otdb_id, modificationTime):
            self._send_filtered_event_message(otdb_id, modificationTime, 'completing')

        def onObservationFinished(self, otdb_id, modificationTime):
            self._send_filtered_event_message(otdb_id, modificationTime, 'finished')

    def __init__(self, exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER):
        super().__init__(handler_type=QAFilteringOTDBBusListener.QAFilteringOTDBEventMessageHandler,
                         exchange=exchange,
                         num_threads=1,
                         broker=broker)


class QAFilteredOTDBBusListener(BusListener):
    class QAFilteredOTDBEventMessageHandler(UsingToBusMixin, OTDBEventMessageHandler):
        '''
        QAFilteredOTDBEventMessageHandler listens on the lofar otdb message bus for NotificationMessages and starts qa processes
        upon observation/pipeline completion. The qa processes convert MS (measurement sets) to hdf5 qa files,
        and then starts generating plots from the hdf5 file.
        '''
        def __init__(self):
            super().__init__()
            self._unfinished_otdb_id_map = {}

        def onObservationCompleting(self, otdb_id, modificationTime):
            '''
            this mehod is called automatically upon receiving a Completion NotificationMessage
            :param int otdb_id: the task's otdb database id
            :param datetime modificationTime: timestamp when the task's status changed to completing
            :return: None
            '''
            logger.info("task with otdb_id %s completed.", otdb_id)

            # immediately do qa when the obs is completing, because the data is already on disk...
            # and do the handling of the feedback in onObservationFinished
            self.do_qa(otdb_id=otdb_id)

        def onObservationFinished(self, otdb_id, modificationTime):
            '''
            this mehod is called automatically upon receiving a Finished NotificationMessage
            :param int otdb_id: the task's otdb database id
            :param datetime modificationTime: timestamp when the task's status changed to finished
            :return: None
            '''
            logger.info("task with otdb_id %s finished. trying to add parset (with feedback) to h5 file", otdb_id)

            # lookup the hdf5_file_path for the given otdb_id
            # and (re)add the parset to the file (which now includes feedback)
            hdf5_file_path = self._unfinished_otdb_id_map.get(otdb_id)
            if hdf5_file_path:
                del self._unfinished_otdb_id_map[otdb_id]

                try:
                    cmd = ['add_parset_to_hdf5', hdf5_file_path]
                    cmd = wrap_command_for_docker(cmd, 'adder', 'latest')
                    cmd = wrap_command_in_cep4_random_node_ssh_call(cmd, partition=SLURM_CPU_PARTITION, via_head=True)

                    logger.info(' '.join(cmd))
                    if call(cmd) == 0:
                        self._copy_hdf5_to_nfs_dir(hdf5_file_path)
                except Exception as e:
                    logger.warning("Cannot add parset with feedback for otdb=%s. error: %s", otdb_id, e)
            else:
                logger.info("Could not find the h5 file for task with otdb_id %s to add the parset to.", otdb_id)

        def do_qa(self, otdb_id):
            '''
            try to do all qa (quality assurance) steps for the given otdb_id
            resulting in an h5 MS-extract file and inspection plots
            :param int otdb_id: observation/pipeline otdb id for which the conversion needs to be done.
            :return: None
            '''

            hdf5_file_path = None

            with OTDBRPC.create(exchange=self.exchange, broker=self.broker, timeout=5) as otdbrpc:
                parset = parameterset(otdbrpc.taskGetSpecification(otdb_id=otdb_id).get("specification", ''))

                if not parset:
                    logger.warning("could not find a parset for otdb_id %s.", otdb_id)
                    return

                if parset.getBool('ObsSW.Observation.DataProducts.Output_Correlated.enabled'):
                    hdf5_file_path = self._convert_ms2hdf5(otdb_id)
                elif parset.getBool('ObsSW.Observation.DataProducts.Output_CoherentStokes.enabled'):
                    hdf5_file_path = self._convert_bf2hdf5(otdb_id)
                else:
                    logger.info("No uv or cs dataproducts avaiblable to convert for otdb_id %s", otdb_id)
                    return

            if hdf5_file_path:
                # keep a note of where the h5 file was stored for this unfinished otdb_id
                self._unfinished_otdb_id_map[otdb_id] = hdf5_file_path

                # cluster it
                self._cluster_h5_file(hdf5_file_path, otdb_id)

                self._copy_hdf5_to_nfs_dir(hdf5_file_path)

                plot_dir_path = self._create_plots_for_h5_file(hdf5_file_path, otdb_id)
                plot_dir_path = self._move_plots_to_nfs_dir(plot_dir_path)

                # and notify that we're finished
                self._send_event_message('Finished', {'otdb_id': otdb_id,
                                                      'hdf5_file_path': hdf5_file_path,
                                                      'plot_dir_path': plot_dir_path or ''})

        def _send_event_message(self, subject_suffix, content):
            try:
                subject = '%s.%s' % (DEFAULT_QA_NOTIFICATION_SUBJECT_PREFIX, subject_suffix)
                msg = EventMessage(subject=subject, content=content)
                logger.info('sending event message %s: %s', subject, content)
                self.send(msg)
            except Exception as e:
                logger.error('Could not send event message: %s', e)

        def _convert_ms2hdf5(self, otdb_id):
            '''
            convert the MS for the given otdb_id to an h5 MS-extract file.
            The conversion will run via ssh on cep4 with massive parellelization.
            When running on cep4, it is assumed that a docker image called adder exists on head.cep4
            When running locally, it is assumed that ms2hdf5 is installed locally.
            :param int otdb_id: observation/pipeline otdb id for which the conversion needs to be done.
            :return string: path to the generated h5 file.
            '''
            try:
                # define default h5 filename use default cep4 qa output dir
                h5_filename = 'L%s.MS_extract.h5' % otdb_id
                h5_dir_path = os.path.join(QA_LUSTRE_BASE_DIR, 'ms_extract')
                hdf5_path = os.path.join(h5_dir_path, h5_filename)

                cmd = ['ls', hdf5_path]
                cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

                if call(cmd) == 0:
                    logger.info('uv dataset with otdb_id %s was already converted to hdf5 file %s', otdb_id, hdf5_path)
                    return hdf5_path

                logger.info('trying to convert MS uv dataset with otdb_id %s if any', otdb_id)
                cmd = ['ms2hdf5', '-o', str(otdb_id), '--cep4', '-p', '-20', '-t', '256']
                cmd += ['--output_dir', h5_dir_path]
                cmd += ['--output_filename', h5_filename]

                # wrap the command in a cep4 docker ssh call
                cmd = wrap_command_for_docker(cmd, 'adder', 'latest')
                cmd = wrap_command_in_cep4_available_node_with_lowest_load_ssh_call(cmd, partition=SLURM_CPU_PARTITION, via_head=True)

                logger.info('starting ms2hdf5, executing: %s', ' '.join(cmd))

                if call(cmd) == 0:
                    logger.info('converted uv dataset with otdb_id %s to hdf5 file %s', otdb_id, hdf5_path)
                    self._send_event_message('ConvertedMS2Hdf5', {'otdb_id': otdb_id, 'hdf5_file_path': hdf5_path})
                    return hdf5_path
                else:
                    msg = 'could not convert dataset with otdb_id %s' % otdb_id
                    logger.error(msg)
                    self._send_event_message('Error', {'otdb_id': otdb_id, 'message': msg})

            except Exception as e:
                logging.exception('error in _convert_ms2hdf5: %s', e)
                self._send_event_message('Error', {'otdb_id': otdb_id, 'message': str(e)})
            return None

        def _create_plots_for_h5_file(self, hdf5_path, otdb_id=None):
            '''
            create plots for the given h5 file. The plots are created via an ssh call to cep4
            where the plots are created in parallel in the docker image.
            :param hdf5_path: the full path to the hdf5 file for which we want the plots.
            :param otdb_id: the otdb_id of the converted observation/pipeline (is used for logging only)
            :return: the full directory path to the directory containing the created plots.
            '''
            try:
                #use default cep4 qa output dir.
                plot_dir_path = os.path.join(QA_LUSTRE_BASE_DIR, 'plots')
                task_plot_dir_path = ''
                all_plots_succeeded = True

                for plot_options in [['-1', '-acb'], # 'hot' autocor/crosscor, per baseline scaling with distinct polarization scales, in dB
                                     ['-1', '-acg'], # 'complex' autocor/crosscor, all baseline scaling with same polarization scales, in dB
                                     ['-1', '-acn', '--raw'], # normalized 'hot' autocor/crosscor, raw
                                     ['-4']]: # delay-rate
                    cmd = ['plot_hdf5_dynamic_spectra', '-o %s' % (plot_dir_path,), '--force', '--cep4'] + plot_options + [hdf5_path]

                    # wrap the command in a cep4 ssh call to docker container
                    cmd = wrap_command_for_docker(cmd, 'adder', 'latest')
                    cmd = wrap_command_in_cep4_available_node_with_lowest_load_ssh_call(cmd, partition=SLURM_CPU_PARTITION, via_head=True)

                    logger.info('generating plots for otdb_id %s, executing: %s', otdb_id, ' '.join(cmd))

                    if call(cmd) == 0:
                        task_plot_dir_path = os.path.join(plot_dir_path, 'L%s' % otdb_id)
                        logger.info('generated plots for otdb_id %s in %s with command=%s', otdb_id,
                                                                                            task_plot_dir_path,
                                                                                            ' '.join(cmd))
                    else:
                        all_plots_succeeded &= False
                        msg = 'could not generate plots for otdb_id %s cmd=%s' % (otdb_id, ' '.join(cmd))
                        logger.error(msg)
                        self._send_event_message('Error', {'otdb_id': otdb_id,
                                                           'message': msg})


                self._send_event_message('CreatedInspectionPlots', {'otdb_id': otdb_id,
                                                                    'hdf5_file_path': hdf5_path,
                                                                    'plot_dir_path': task_plot_dir_path})
                return task_plot_dir_path
            except Exception as e:
                logging.exception('error in _create_plots_for_h5_file: %s', e)
                self._send_event_message('Error', {'otdb_id': otdb_id, 'message': str(e)})
            return None

        def _convert_bf2hdf5(self, otdb_id):
            '''
            convert the beamformed h5 dataset for the given otdb_id to an h5 MS-extract file.
            When running on cep4, it is assumed that a docker image called adder exists on head.cep4
            When running locally, it is assumed that ms2hdf5 is installed locally.
            :param int otdb_id: observation/pipeline otdb id for which the conversion needs to be done.
            :return string: path to the generated h5 file.
            '''
            try:
                # define default h5 filename use default cep4 qa output dir
                h5_filename = 'L%s.MS_extract.h5' % otdb_id
                h5_dir_path = os.path.join(QA_LUSTRE_BASE_DIR, 'ms_extract')
                hdf5_path = os.path.join(h5_dir_path, h5_filename)

                cmd = ['ls', hdf5_path]
                cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

                if call(cmd, stdout=None, stderr=None) == 0:
                    logger.info('bf dataset with otdb_id %s was already converted to hdf5 file %s', otdb_id, hdf5_path)
                    return hdf5_path

                logger.info('trying to convert beamformed dataset with otdb_id %s if any', otdb_id)

                cmd = ['bf2hdf5', '-o', str(otdb_id)]
                cmd += ['--output_dir', h5_dir_path]
                cmd += ['--output_filename', h5_filename]

                # wrap the command in a cep4 docker ssh call
                cmd = wrap_command_for_docker(cmd, 'adder', 'latest')
                cmd = wrap_command_in_cep4_available_node_with_lowest_load_ssh_call(cmd, partition=SLURM_CPU_PARTITION, via_head=True)

                logger.info('starting bf2hdf5, executing: %s', ' '.join(cmd))

                if call(cmd) == 0:
                    hdf5_path = os.path.join(h5_dir_path, h5_filename)
                    logger.info('converted bf dataset with otdb_id %s to hdf5 file %s', otdb_id, hdf5_path)
                    self._send_event_message('ConvertedBF2Hdf5', {'otdb_id': otdb_id, 'hdf5_file_path': hdf5_path})
                    return hdf5_path
                else:
                    msg = 'could not convert dataset with otdb_id %s' % otdb_id
                    logger.error(msg)
                    self._send_event_message('Error', {'otdb_id': otdb_id, 'message': msg})

            except Exception as e:
                logging.exception('error in _convert_ms2hdf5: %s', e)
                self._send_event_message('Error', {'otdb_id': otdb_id, 'message': str(e)})
            return None

        def _copy_hdf5_to_nfs_dir(self, hdf5_path):
            try:
                hdf5_filename = os.path.basename(hdf5_path)
                hdf5_nfs_path = os.path.join(QA_NFS_BASE_DIR, 'h5', hdf5_filename)
                cmd = ['cp', hdf5_path, hdf5_nfs_path]
                cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

                logger.debug('copying h5 file to nfs dir: %s', ' '.join(cmd))
                if call(cmd) == 0:
                    logger.info('copied h5 file to nfs dir: %s -> %s', hdf5_path, hdf5_nfs_path)
                    return hdf5_nfs_path
            except Exception as e:
                logging.exception('error in _copy_hdf5_to_nfs_dir: %s', e)

        def _move_plots_to_nfs_dir(self, plot_dir_path):
            try:
                plot_dir_name = os.path.basename(plot_dir_path)
                plot_nfs_path = os.path.join(QA_NFS_BASE_DIR, 'plots', plot_dir_name)
                cmd = ['cp', '-rf', plot_dir_path, plot_nfs_path]
                cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

                logger.info('copying plots: %s', ' '.join(cmd))
                if call(cmd) == 0:
                    logger.info('copied plots from %s to nfs dir: %s', plot_dir_path, plot_nfs_path)

                    cmd = ['rm', '-rf', plot_dir_path]
                    cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

                    logger.debug('removing plots: %s', ' '.join(cmd))
                    if call(cmd) == 0:
                        logger.info('removed plots from %s after they were copied to nfs dir %s', plot_dir_path, plot_nfs_path)
                        return plot_nfs_path
            except Exception as e:
                logging.exception('error in _copy_hdf5_to_nfs_dir: %s', e)

        def _cluster_h5_file(self, hdf5_path, otdb_id=None):
            '''
            Try to cluster the baselines based on visibilities in the h5 file
            using the clustering docker image developed by e-science.
            This method assumes the adder_clustering docker image is available on cep4. If not, or if anything else
            goes wrong, then the qa steps can just continue on the un-clustered h5 file.
            The docker image can be build from the source on github:
            https://github.com/NLeSC/lofar-predictive-maintenance
            This is a private repo until the project has been published. At astron, jorrit has access.
            In the future, we might incorporate the clustering code from the github repo in to the LOFAR source tree.
            :param hdf5_path: the full path to the hdf5 file for which we want the plots.
            :param otdb_id: the otdb_id of the converted observation/pipeline (is used for logging only)
            :return: None
            '''
            try:
                cmd = ['show_hdf5_info', hdf5_path, '|', 'grep', 'clusters']
                cmd = wrap_command_for_docker(cmd, 'adder', 'latest')
                cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

                if call(cmd) == 0:
                    logger.info('hdf5 file %s otdb_id %s was already clustered', hdf5_path, otdb_id)
                    return

                # the command to cluster the given h5 file (executed in the e-science adder docker image)
                cmd = ['cluster_this.py', hdf5_path]
                cmd = wrap_command_for_docker(cmd, 'adder_clustering', 'latest')
                cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

                logger.info('clustering hdf5 file %s otdb_id %s, executing: %s', hdf5_path, otdb_id, ' '.join(cmd))

                if call(cmd) == 0:
                    logger.info('clustered hdf5 file %s otdb_id %s', hdf5_path, otdb_id)

                    self._send_event_message('Clustered', {'otdb_id': otdb_id,
                                                           'hdf5_file_path': hdf5_path})
                else:
                    msg = 'could not cluster hdf5 file %s otdb_id %s' % (hdf5_path, otdb_id)
                    logger.error(msg)
                    self._send_event_message('Error', {'otdb_id': otdb_id, 'message': msg})
            except Exception as e:
                logging.exception('error in _cluster_h5_file: %s', e)
                self._send_event_message('Error', {'otdb_id': otdb_id, 'message': str(e)})

    def __init__(self, exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER):
        super().__init__(handler_type=QAFilteredOTDBBusListener.QAFilteredOTDBEventMessageHandler,
                         handler_kwargs={},
                         exchange=exchange,
                         routing_key="%s.#" % (DEFAULT_FILTERED_OTDB_NOTIFICATION_SUBJECT,),
                         num_threads=1,
                         broker=broker)

class QAService:
    def __init__(self, exchange: str=DEFAULT_BUSNAME, broker: str=DEFAULT_BROKER):
        """
        :param exchange: valid message exchange address
        :param broker: valid broker host (default: None, which means localhost)
        """
        self.filtering_buslistener = QAFilteringOTDBBusListener(exchange = exchange, broker = broker)
        self.filtered_buslistener = QAFilteredOTDBBusListener(exchange = exchange, broker = broker)

    def __enter__(self):
        self.filtering_buslistener.start_listening()
        self.filtered_buslistener.start_listening()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.filtering_buslistener.stop_listening()
        self.filtered_buslistener.stop_listening()

def main():
    '''
    Run the qa service program with commandline arguments.
    '''

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='run the qa_service which listens for observations/pipelines finished events on '
                                      'the bus and then starts the QA (Quality Assurance) processes to convert MS to '
                                      'hdf5 files and generate inspection plots.')
    group = OptionGroup(parser, 'QPid Messaging options')
    group.add_option('-b', '--broker', dest='broker', type='string', default='localhost', help='Address of the qpid broker, default: %default')
    group.add_option('-e', "--exchange", dest="exchange", type="string",
                      default=DEFAULT_BUSNAME,
                      help="Bus or queue where the OTDB notifications are published. [default: %default]")
    parser.add_option_group(group)
    (options, args) = parser.parse_args()

    #config logging
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    #start the qa service
    with QAService(exchange=options.exchange, broker=options.broker):
        #loop and wait for messages or interrupt.
        waitForInterrupt()

if __name__ == '__main__':
    main()
