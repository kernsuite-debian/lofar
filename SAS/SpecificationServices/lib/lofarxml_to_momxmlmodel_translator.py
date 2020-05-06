#!/usr/bin/env python3

# lofarxml_to_momxmlmodel_translator.py
#
# Copyright (C) 2017
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

from lxml import etree
from io import BytesIO

from lofar.specificationservices.telescope_model import TelescopeModel
from lofar.specificationservices.specification_service import _parse_relation_tree


class LofarXMLToMomXMLModelTranslator(object):
    def generate_model(self, lofar_spec):
        doc = etree.parse(BytesIO(lofar_spec.encode('UTF-8')))

        project_codes = doc.xpath('/spec:specification/projectReference/ProjectCode',
                                  namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        project_name = project_codes[0].text

        if project_name == "LC7_030" or project_name == "test-lofar":
            model = TelescopeModel()

            model.start_time = self._get_start_time(doc)
            model.end_time = self._get_start_time(doc)
            model.min_start_time = self._get_min_start_time(doc)
            model.max_end_time = self._get_max_end_time(doc)
            model.duration = self._get_duration(doc)
            model.min_duration = self._get_min_duration(doc)
            model.max_duration = self._get_max_duration(doc)
            model.target_ra = self._get_target_ra(doc)
            model.target_dec = self._get_target_dec(doc)
            model.calibrator_ra = self._get_calibrator_ra(doc)
            model.calibrator_dec = self._get_calibrator_dec(doc)
            model.trigger_id = self._get_trigger_id(doc)
            model.station_selection, model.custom_station_list = self._get_station_selection_and_list(doc)
            model.outer_foldername = self._get_outer_foldername(doc)
            model.inner_foldername = self._get_inner_foldername(doc)
            model.projectname = project_name

            return model
        else:
            raise NotImplementedError

    def _get_start_time(self, doc):
        start_times = doc.xpath('/spec:specification/activity/observation/timeWindowSpecification/startTime',
                                namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        if start_times:
            return start_times[0].text
        else:
            return None

    def _get_min_start_time(self, doc):
        min_start_times = doc.xpath('/spec:specification/activity/observation/timeWindowSpecification/minStartTime',
                                namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        if min_start_times:
            return min_start_times[0].text
        else:
            return None

    def _get_max_end_time(self, doc):
        max_end_times = doc.xpath('/spec:specification/activity/observation/timeWindowSpecification/maxEndTime',
                                namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        if max_end_times:
            return max_end_times[0].text
        else:
            return None

    def _get_min_duration(self, doc):
        min_duration = doc.xpath('/spec:specification/activity/observation/timeWindowSpecification/duration/minimumDuration',
                                namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        if min_duration:
            return min_duration[0].text
        else:
            return None

    def _get_max_duration(self, doc):
        max_duration = doc.xpath('/spec:specification/activity/observation/timeWindowSpecification/duration/maximumDuration',
                                namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        if max_duration:
            return max_duration[0].text
        else:
            return None

    def _get_duration(self, doc):
        durations = doc.xpath('/spec:specification/activity/observation/timeWindowSpecification/duration/duration',
                              namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        if durations:
            return durations[0].text
        else:
            return None

    def _get_station_selection_and_list(self, doc):
        """
        Parses the station selection specificatoon and returns a dict with resource groups and min values as well as
        a list of station names parsed from the custom station set. These custom stations are also already included
        in the resourcegroup dictionary with minimum value 1.
        """
        selections = doc.xpath('/spec:specification/activity/observation/stationSelectionSpecification/stationSelection',
                              namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        station_selection = {}
        station_list = []
        for selection in selections:
            station_set = selection.xpath("stationSet")[0].text
            if station_set == "Custom":
                stations = selection.xpath("stations/station")
                for station in stations:
                    stationname = station.xpath("name")[0].text
                    station_selection.update({stationname: 1})
                    station_list.append(stationname)

            else:
                min_constraint = selection.xpath("minimumConstraint")[0].text
                station_selection.update({station_set: min_constraint})

        return station_selection, station_list

    def _get_target_ra(self, doc):
        target_beam = self._get_target_beam(doc)
        return target_beam.xpath("ra")[0].text

    def _get_target_dec(self, doc):
        target_beam = self._get_target_beam(doc)
        return target_beam.xpath("dec")[0].text

    def _get_calibrator_ra(self, doc):
        target_beam = self._get_calibrator_beam(doc)
        return target_beam.xpath("ra")[0].text

    def _get_calibrator_dec(self, doc):
        target_beam = self._get_calibrator_beam(doc)
        return target_beam.xpath("dec")[0].text

    def _get_target_beam(self, doc):
        return self._get_beam(doc, "Target")

    def _get_calibrator_beam(self, doc):
        return self._get_beam(doc, "Calibrator")

    def _get_beam(self, doc, beam_name):
        beam_measurements = doc.xpath('/spec:specification/activity/measurement[@xsi:type="base:SAPMeasurement"]',
                                      namespaces={"spec": "http://www.astron.nl/LofarSpecification",
                                                  "xsi": "http://www.w3.org/2001/XMLSchema-instance"})

        for beam_measurement in beam_measurements:
            name = beam_measurement.xpath("name")
            if name[0].text == beam_name:
                return beam_measurement

    def _get_trigger_id(self, doc):
        identifier = doc.xpath('/spec:specification/activity/triggerId/identifier',
                               namespaces={"spec": "http://www.astron.nl/LofarSpecification"})

        return int(identifier[0].text)

    def _get_folder_relations_and_names(self, doc):
        """
        parses folder relations and returns two dicts to look up parent folder and folder name for a given folder id
        :param doc: ElementTree
        :return: (dict, dict)
        """
        spec = doc.getroot()
        _, parentfolders, foldernames = _parse_relation_tree(spec)
        return parentfolders, foldernames

    def _get_inner_foldername(self, doc):
        """
        determine inner folder name for type 1 lofar specs
        :param doc: ElementTree
        :return: string
        """
        parentfolders, foldernames = self._get_folder_relations_and_names(doc)
        # parentfolders contains key-value pairs of folder-folder relations
        # type 1 triggers only have one inner folder (so the following does not work for type 2)
        if len(parentfolders) == 0:
            raise Exception('There seems to be no inner folder!')
        if len(parentfolders) > 1:
            raise Exception('There seems to be more than one inner folder: ' + str(list(parentfolders.keys())))
        inner_folder_key = list(parentfolders.keys())[0]
        name = foldernames[inner_folder_key]
        return name

    def _get_outer_foldername(self, doc):
        """
        determine outermost folder name in lofar specs
        :param doc: ElementTree
        :return: string
        """
        parentfolders, foldernames = self._get_folder_relations_and_names(doc)
        # parentfolders contains key-value pairs of folder-folder relations
        # trigger templates only allow for one outer folder (this should work for types 1 and 2)
        if len(parentfolders) == 0:
            raise Exception('There seems to be no outer folder!')
        if not all(value == list(parentfolders.values())[0] for value in list(parentfolders.values())):
            # there are folders with different parents, i.e. there is a deeper hierarchy or several parent folders.
            raise Exception('There seems to be more then one outer folder: ' + str(list(parentfolders.values())))
        outer_folder_key = list(parentfolders.values())[0]
        name = foldernames[outer_folder_key]
        return name
