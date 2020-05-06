#!/usr/bin/env python3

# telescope_model_xml_generator_type1.py
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

import os
from lxml import etree
from io import BytesIO
from .config import TELESCOPE_MODEL_TYPE1_XML
import json
from collections import OrderedDict

from lofar.specificationservices.telescope_model import TelescopeModel


class TelescopeModelException(Exception):
    pass


class TelescopeModelXMLGeneratorType1(object):
    def get_xml_tree(self, telescope_model):
        template_file_path = os.path.expandvars(TELESCOPE_MODEL_TYPE1_XML)
        template = self._read_telescope_model_template(template_file_path)
        xmldoc = etree.parse(BytesIO(template.encode('UTF-8')))

        if not isinstance(telescope_model, TelescopeModel):
            raise TelescopeModelException("No telescope model of type TelescopeModel provided")

        root_element = xmldoc.getroot()
        self._set_start_time(root_element, telescope_model.start_time)
        self._set_duration(root_element, telescope_model.duration)
        self._set_target_ra(root_element, telescope_model.target_ra)
        self._set_target_dec(root_element, telescope_model.target_dec)
        self._set_calibrator_ra(root_element, telescope_model.calibrator_ra)
        self._set_calibrator_dec(root_element, telescope_model.calibrator_dec)
        self._add_trigger_id_to_misc(root_element, telescope_model.trigger_id)
        self._add_time_window_to_misc(root_element,
                                      telescope_model.min_start_time,
                                      telescope_model.max_end_time,
                                      telescope_model.min_duration,
                                      telescope_model.max_duration)
        self._add_station_selection_to_misc(root_element, telescope_model.station_selection)
        self._set_stations(root_element, telescope_model.custom_station_list)
        self._set_inner_foldername(root_element, telescope_model.inner_foldername )
        self._set_outer_foldername(root_element, telescope_model.outer_foldername)
        self._set_projectname(root_element, telescope_model.projectname)

        return xmldoc

    @staticmethod
    def _read_telescope_model_template(template_path):
        with open(template_path, "r") as f:
            template = f.read()
        return template

    @staticmethod
    def _set_start_time(element, start_time):
        user_spec = element.find(".//userSpecification")
        _start_time = user_spec.find("startTime")

        if start_time:
            _start_time.text = start_time
        else:
            user_spec.remove(_start_time)

    @staticmethod
    def _set_duration(element, duration):
        _user_spec = element.find(".//userSpecification")
        _duration = _user_spec.find("duration")

        if duration:
            _duration.text = duration
        else:
            _user_spec.remove(_duration)

    def _set_target_ra(self, element, ra):
        measurement = self._get_specification_by_name(element, "Target")
        _ra = measurement.find("ra")
        _ra.text = ra

    def _set_target_dec(self, element, dec):
        measurement = self._get_specification_by_name(element, "Target")
        _dec = measurement.find("dec")
        _dec.text = dec

    def _set_calibrator_ra(self, element, ra):
        measurement = self._get_specification_by_name(element, "Calibrator")
        _ra = measurement.find("ra")
        _ra.text = ra

    def _set_calibrator_dec(self, element, dec):
        measurement = self._get_specification_by_name(element, "Calibrator")
        _dec = measurement.find("dec")
        _dec.text = dec

    def _add_to_misc(self, element, to_add):
        """
        adds dict to_add to all misc fields
        Note: will not traverse, so dict keys should not be present already!
        """
        miscs = element.findall(".//misc")
        for misc in miscs:
            if misc.text:
                m = json.loads(misc.text, object_pairs_hook=OrderedDict)
            else:
                m = OrderedDict() 
            m.update(to_add)
            misc.text = json.dumps(m)

    def _add_trigger_id_to_misc(self, element, trigger_id):
        t = {"trigger_id": trigger_id}
        self._add_to_misc(element, t)

    def _add_station_selection_to_misc(self, element, station_selection):
        if station_selection:
            groups = []
            for resource_group, minimum in sorted(station_selection.items()):
                groups.append(OrderedDict([("resourceGroup", resource_group),("min", minimum)]))
            s = {"stationSelection": groups}
            self._add_to_misc(element, s)

    def _add_time_window_to_misc(self, element, min_start_time, max_end_time, min_duration, max_duration):
        items = OrderedDict() 
        if min_start_time:
            items.update({'minStartTime': min_start_time})
        if max_end_time:
            items.update({'maxEndTime': max_end_time})
        if min_duration:
            items.update({'minDuration': min_duration})
        if max_duration:
            items.update({'maxDuration': max_duration})
        if len(items) > 0:
            tw = {'timeWindow': items}
            self._add_to_misc(element, tw)

    @staticmethod
    def _set_stations(element, station_list):
        """
        This takes a list of station names and replaces the current set under .//userSpecification.stations.
        """
        user_spec = element.find(".//userSpecification")
        stations = user_spec.find("stations")

        # remove all existing station elements
        for station in stations.xpath('station'):
            stations.remove(station)

        # add new ones
        if station_list:
            for stationname in station_list:
                station = etree.Element('station', name=stationname)
                stations.append(station)

    def _set_inner_foldername(self, element, foldername):
        """
        set name on first sub-folder in first folder on element (inner folder on type 1 template)
        """
        folder = element.find('.//lofar:folder', namespaces=element.nsmap)
        innerfolder = folder.find('.//lofar:folder', namespaces=element.nsmap)
        innerfolder.find('name').text = foldername

    def _set_outer_foldername(self, element, foldername):
        """
        set name on first folder on element
        """
        folder = element.find('.//lofar:folder', namespaces=element.nsmap)
        folder.find('name').text = foldername

    def _set_projectname(self, element, projectname):
        """
        set text on all projectName elements and on project.name
        """
        pnames = element.findall('.//projectName')
        for pname in pnames:
            pname.text = projectname

        element.find('name').text = projectname

    @staticmethod
    def _get_specification_by_name(element, name):
        specifications = element.findall(".//specification")

        for s in specifications:
            for e in s.iter():
                if e.tag == "targetName" and e.text == name:
                    return s

