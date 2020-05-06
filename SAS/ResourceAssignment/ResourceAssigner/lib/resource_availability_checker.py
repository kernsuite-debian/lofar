#!/usr/bin/env python3

# Copyright (C) 2015-2017
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

"""
ResourceAvailabilityChecker checks whether requested resources can be claimed or not
"""

from lofar.common.cache import cache

import logging

logger = logging.getLogger(__name__)

class CouldNotFindClaimException(Exception):
    pass


class ResourceAvailabilityChecker(object):
    def __init__(self, radb):
        self.radb = radb

    @property
    @cache
    def resource_group_relations(self):
        """ Returns a dict of resource groups and their relations. Does not include resources.

            Each dict element has the resource group id as key, and the following value:

            { "child_ids":  list of child resource groups
              "parent_ids": list of parent resource groups
              "resource_ids": list of resources in this group. } """

        memberships = self.radb.getResourceGroupMemberships()
        return memberships['groups']  # resource-group-to-resource-group relations

    @property
    @cache
    def resource_types(self):
        """ Returns a dict of all the resource types, to convert name->id. """

        return {rt['name']: rt['id'] for rt in self.radb.getResourceTypes()}

    @property
    @cache
    def resource_claim_property_types(self):
        """ Returns a dict of all the resource claim property types, to convert name->id. """

        return {rcpt['name']: rcpt['id'] for rcpt in self.radb.getResourceClaimPropertyTypes()}

    @cache
    def _summable_property_type_ids(self):
        dtypes = {'uv', 'cs', 'is', 'im', 'img', 'pulp'}
        return {self.resource_claim_property_types['nr_of_' + dt + '_files'] for dt in dtypes}

    # find a fit, with the following guarantees:
    #	1) find a fit if possible
    #	2) create conflicting claims on available resources if not
    #	3) if no resource available at all, raise an exception
    #	4) annotate claims with claim["requested_resources"] == [requested_resources for this claim]
    #      for each claim (one claim can cover multiple estimates)
    def get_is_claimable(self, requested_resources, available_resources):
        """
        Verify if the requested resources can be claimed and construct tentative claim objects for them. Note that these
        objects are not inserted into the RADB - this is left to the caller.

        :param requested_resources: The requested resources
        :param available_resources: The available resources

        :returns A list of tentative resource claim objects if all requested resources are claimable

        :raises CouldNotFindClaimException exception if one or more of the requested resources are not claimable
        """

        # This function selects resources for a task (i.e. obs or pipeline). Keep it side-effect free!
        # Criteria:
        # * It all fits within max fill ratio per resource group (or consider failed)
        # * Avoid resources marked as unavailable
        # * At most one claim per resource; i.e. merge where possible (DB friendly)
        # * Most pipelines reduce data size. Observation output is relatively large,
        #   so spread across as many storage areas as possible (if storage is needed).
        # * Only completely fill a (e.g. storage) resource when inevitable, as this also makes other
        #   resources (e.g. write bandwidth) unavailable for future tasks until clean up.
        # * All 4 data products of complex voltage obs data (XXYY) go to a single (storage) resource.
        #
        # Parts of these criteria may be solved by the caller, e.g. by passing filtered arguments.
        #
        # Note: certain (obs) settings are more flexible than ever used (e.g. sb list per SAP for CS/IS).
        # We must support the full gamut of settings, but for scenarios that are complex *and* constrained,
        # producing 'conflict' may be ok, if this saves implementation or excessive computational complexity.
        # Users will then have to free more resources than strictly necessary before retrying.

        logger.debug('get_is_claimable: current_resource_usage: %s', available_resources)  # big!

        claims = []
        for requested_resource in requested_resources:
            needed_resources_by_type_id = self._get_resource_types_by_type_id(requested_resource)

            claimable_resources = self._get_availability_of_requested_resources(
                requested_resource['root_resource_group'],
                needed_resources_by_type_id,
                available_resources
            )

            file_properties = self._get_resources_files_properties(requested_resource)

            self._collapse_requested_resources(requested_resource, needed_resources_by_type_id, claimable_resources,
                                               file_properties)

            more_claims = self._get_tentative_claim_objects_for_multiple_resources(needed_resources_by_type_id,
                                                                                   requested_resource['resource_count'],
                                                                                   claimable_resources)

            # add resource properties
            for claim in more_claims:
                # annotate with the requested resources
                claim["requested_resources"] = [requested_resource]

                # the 'file_properties' should only be added to storage resources,
                # as they encode the size of the files
                if claim['resource_type_id'] == self.resource_types['storage']:
                    claim['properties'] = file_properties

            # add to the list of claims
            claims.extend(more_claims)

        self._merge_claims(claims)

        return claims

    def _get_current_resource_usage(self):
        db_resource_list = self.radb.getResources(include_availability=True)
        db_resource_max_fill_ratios = self.radb.getResourceAllocationConfig(sql_like_name_pattern='max_fill_ratio_%')

        self._apply_maximum_fill_ratios(db_resource_list, db_resource_max_fill_ratios)

        return db_resource_list

    def _get_resource_types_by_type_id(self, resource):
        # Replace resource names by type ids: easy matching w/ other data structs
        needed_resources_by_type_id = {
            # e.g. {3: 16536, 5: 170016}
            self.resource_types[name]: resource['resource_types'][name] for name in resource['resource_types']
        }
        logger.info('get_is_claimable: needed_resources_by_type_id: %s', needed_resources_by_type_id)

        return needed_resources_by_type_id

    # TODO: look at claimable capacity instead of available capacity?
    def _get_availability_of_requested_resources(self, root_resource_group, needed_resources_by_type_id, current_resource_usage):
        # Find group id ('gid') of needed_resources['root_resource_group'],
        # then get list of claimable resources at root_gid and its children
        root_gid = self._get_resource_group_id_by_name(root_resource_group)

        # e.g. [{3: <resource_dict>, 5: <resource_dict>}, ...]
        requested_resource_availability = self._get_subtree_resources_list(root_gid, needed_resources_by_type_id,
                                                                           current_resource_usage)
        logger.info('get_is_claimable: considering %d available resource dict(s)', len(requested_resource_availability))
        logger.debug('get_is_claimable: requested_resource_availability: %s', requested_resource_availability)

        return requested_resource_availability

    def _get_resources_files_properties(self, needed_resources):
        """ Return all the file properties of a given set of resources (if any). """

        input_files = needed_resources.get('input_files')
        output_files = needed_resources.get('output_files')
        properties = self._get_files_properties(input_files, 'input')
        properties.extend(self._get_files_properties(output_files, 'output'))

        return properties

    def _collapse_requested_resources(self, resource, needed_resources_by_type_id, claimable_resources,
                                      file_properties):
        """
        Collapses the requested resources when there is only 1 available resource dict, e.g. global filesystem
        """
        if len(claimable_resources) == 1:
            logger.info('get_is_claimable: collapsing needed_resources')
            for type_id in needed_resources_by_type_id:
                needed_resources_by_type_id[type_id] *= resource['resource_count']
            for property in file_properties:
                if property['type'] in self._summable_property_type_ids():
                    property['value'] *= resource['resource_count']
            resource['resource_count'] = 1

    def _apply_maximum_fill_ratios(self, db_resource_list,
                                   db_resource_max_fill_ratios):
        ''' Applies db_resource_max_fill_ratios to db_resource_list.
            db_resource_max_fill_ratios is e.g. [{'name': max_fill_ratio_CEP4_storage, 'value': 0.85}, ...]
        '''
        prefix = 'max_fill_ratio_'  # + resource_group_name + '_' + resource_type_name

        for ratio_dict in db_resource_max_fill_ratios:
            for res_type_name, res_type_id in self.resource_types.items():
                if not ratio_dict['name'].endswith('_' + res_type_name):
                    continue
                res_group_name = ratio_dict['name'][len(prefix) : -len(res_type_name)-1]
                res_group_id = self._get_resource_group_id_by_name(res_group_name)

                res_group = self.resource_group_relations[res_group_id]
                for res_id in res_group['resource_ids']:
                    res = db_resource_list[res_id]
                    if res['type_id'] != res_type_id:
                        continue
                    try:
                        ratio = float(ratio_dict['value'])
                    except ValueError as err:
                        logger.error('applyMaxFillRatios: %s = %s: %s', ratio_dict['name'], ratio_dict['value'], str(err))
                        break
                    if ratio < 0.0 or ratio > 1.0:
                        logger.error('applyMaxFillRatios: %s = %s: value not in range [0.0, 1.0]', ratio_dict['name'], ratio)
                        break

                    if 'available_capacity' in res:
                        res['available_capacity'] = min(res['available_capacity'], int(ratio * res['total_capacity']))
                    if 'claimable_capacity' in res:
                        res['claimable_capacity'] = min(res['claimable_capacity'], int(ratio * res['total_capacity']))
                    logger.info('applyMaxFillRatios: applied %s = %f', ratio_dict['name'], ratio)

    def _get_tentative_claim_objects_for_multiple_resources(self, needed_resources_by_type_id, resource_count,
                                                            claimable_resources_list):
        """
        Find a fit for multiple needed resources and create a tentative claim object for them. Modifies
        claimable_resources_list with a lower resource availability with respect to the claims made (also if no claims
        are made!).

        :param needed_resources_by_type_id: The ID of the resource type to claim resources for
        :param resource_count:              The number of times each of the resource should be carried out
        :param claimable_resources_list:    The current list of available/claimable resources

        :returns A list of tentative claim objects for the given needed resources

        :raises CouldNotFindClaimException if no tentative claim object could be made
        """

        claims = []
        for _ in range(resource_count):
            # try to fit a single resource set
            more_claims = self._get_tentative_claim_objects_for_single_resource(needed_resources_by_type_id, claimable_resources_list)

            logger.debug('fit_multiple_resources: added claim: %s', more_claims)

            # add it to our list
            claims.extend(more_claims)

        logger.info('fit_multiple_resources: created claims: %s', claims)

        return claims

    def _get_tentative_claim_objects_for_single_resource(self, needed_resources_by_type_id, claimable_resources_list):
        """
        Find a fit for a single needed resource set. Reorders claimable_resources_list and reduces the resource
        availability in claimable_resources_list with the size of the resulting claims.

        :param needed_resources_by_type_id: the ID of the resource type to find a fit for
        :param claimable_resources_list:    a list of all resources we are allowed to claim, f.e. all DRAGNET disks or
                                            all stations.

        :return A list of created tentative claims objects

        :raises CouldNotFindClaimException if no tentative claim object could be made
        """

        # If no resources are available, we cannot return any claim
        if not claimable_resources_list:
            # rcu resource type is an exception. it needs to be treated differently. Discussed with AK and JD,
            # rcu is currently the only resource which needs a different availability check (bitwise vs claimsize<available)
            # outcome of discussion: do not make rcu an exception, but allow a different comparison strategy for each type of resource.
            # TODO: make comparison strategy generic.
            if set(needed_resources_by_type_id.keys()) == set([self.resource_types['rcu']]):
                return []
            else:
                #for all non-rcu types, the claimable_resources_list should not be empty
                raise CouldNotFindClaimException("No claimable resources given while creating tentative claims for %s" % (needed_resources_by_type_id,))

        if self.resource_types['storage'] in needed_resources_by_type_id:
            sort_res_type = self.resource_types['storage']
        else:
            sort_res_type = list(needed_resources_by_type_id.keys())[0]  # some other if not storage

        # Try to fit first where there is the most space. We first look for space within the unclaimed
        # resources (=free - claimed - our claims), we then look for a fit if no tasks were running
        # (=free - our claims), allowing conflict resolution to help with that later on.
        claims = None

        for capacity_type in ('claimable_capacity', 'available_capacity'):
            # Sorting on every change may be slow, but for 100s of DPs, insertion of merged claims is still 3-5x slower.
            # A heapq was not faster, yet solving the lack of total ordering more elaborate.
            # Of course, big-O complexity here is terrible, but we are nowhere near (too) big.
            claimable_resources_list.sort(key=lambda res: res[sort_res_type][capacity_type], reverse=True)

            # Almost always iterates once. Still needed to match >1 resource types. For example, if we schedule
            # storage and bandwidth simultaneously, our sorting may not put a usable combination in the first slot,
            # as we sort on only one of their capacities (storage).
            for claimable_resources_dict in claimable_resources_list:
                if self._is_claimable_capacity_wise(needed_resources_by_type_id,
                                                    claimable_resources_dict,
                                                    capacity_type,
                                                    ignore_type_ids=[self.resource_types['rcu']]):
                    claims = self._construct_tentative_claim_object(needed_resources_by_type_id,
                                                                    claimable_resources_dict)

                if claims is not None:
                    # Found a fit
                    break

            if claims is not None:
                # Found a fit
                break

        if claims is None:
            # it is allowed/expected for 'rcu' resource_type not to create any tentative claims (see above for comparison stategy remarks)
            # else, raise a CouldNotFindClaimException
            if set(needed_resources_by_type_id.keys()) != set([self.resource_types['rcu']]):
                # Could not find a fit in any way
                raise CouldNotFindClaimException("No resources available of the given type with sufficient capacity. needed_resources_by_type_id=%s claimable_resources_list=%s" % (needed_resources_by_type_id, claimable_resources_list))
        else:
            logger.debug('fit_single_resources: created claims: %s', claims)
            # UGLY: claimable_resources_dict is the last claimable_resources_dict while looping over claimable_resources_list, when we found a claim.
            # not very nice, name scoping wise...
            self._reduce_resource_availability(claimable_resources_dict, claims)

        return claims

    def _get_resource_group_id_by_name(self, name):
        """ Returns group id of resource group named name, or raises a ValueError if name was not found.
            The search happens breadth-first.
        """
        gids = [0]  # root group id 0. The next disabled line is more generic, but better cache it.
        # gids = [gid for gid, group in self.resource_group_relations.items() if not group['parent_ids']]  # roots have empty parent list; normally we have 1 root

        i = 0
        while i < len(gids):  # careful iterating while modifying
            res_group = self.resource_group_relations[gids[i]]
            if res_group['resource_group_name'] == name:
                return gids[i]
            gids.extend(res_group['child_ids'])
            i += 1

        raise ValueError(
            'getResourceGroupIdByName: cannot find resources to claim: unknown root_resource_group \'%s\'' % name)

    def _get_subtree_resources_list(self, root_gid, needed_resources_by_type_id, db_resource_list):
        """ Returns list of available resources of type id in needed_resources_by_type_id.keys()
            starting at group id root_gid in the format [{type_id: {<resource_dict>}, ...}, ...].
        """
        # Replace list of dicts to a dict of dicts because rid is not garanteed the correct index
        # of the list.
        available_recources = {r["id"]:r for r in db_resource_list}

        # Search breadth-first starting at root_gid.
        gids = [root_gid]
        resources_list = []

        i = 0
        while i < len(gids):  # careful iterating while modifying
            resources = {}
            type_ids_seen = set()

            res_group = self.resource_group_relations[gids[i]]
            for rid in res_group['resource_ids']:
                if rid in available_recources:
                    available_recource = available_recources[rid]
                    type_id = available_recource['type_id']
                    if type_id in needed_resources_by_type_id and available_recource['active']:
                        if available_recource['available_capacity'] > 0:
                            resources[type_id] = available_recource
                            type_ids_seen.add(type_id)
                else:
                    logger.debug("requested resource id %s is not available/claimable", rid)

            # Only add resource IDs if all needed types are present in this resource group
            if type_ids_seen == set(needed_resources_by_type_id):
                resources_list.append(resources)

            gids.extend(res_group['child_ids'])
            i += 1

        return resources_list

    def _is_claimable_capacity_wise(self, needed_resources, claimable_resources, capacity_type, ignore_type_ids=None):
        """ Returns whether all needed_resources can be claimed from claimable_resources.

            :param needed_resources:    {resource_type_id: size, ...}
            :param claimable_resources: {resource_type_id: {<resource_dict>}, ...}
            :param capacity_type        type of capacity to consider ('available_capacity' or 'claimable_capacity')
            :param ignore_type_ids:     IDs of types that should not be considered
        """
        types_to_ignore = ignore_type_ids if ignore_type_ids is not None else []

        is_claimable = all(claim_size <= claimable_resources[res_type][capacity_type]
                           for res_type, claim_size in list(needed_resources.items()) if res_type not in types_to_ignore)

        return is_claimable

    def _construct_tentative_claim_object(self, needed_resources, claimable_resources):
        """ Returns list of claims for a data product (one for each needed resource type).

            Format needed_resources:    {resource_type_id: size, ...}
            Format claimable_resources: {resource_type_id: {<resource_dict>}, ...}

            For a complete claim object to send to RADB, the following fields need to be set for
            each claim returned by makeClaim:
                starttime, endtime, properties (optional)
        """
        claims = []

        for res_type, claim_size in list(needed_resources.items()):
            # claim starttime/endtime is needed by RADB, but will be annotated later in tieClaimsToTask.
            # We do this to separate responsibilities. The scheduling functions (get_is_claimable and helpers)
            # only depend on the available resources (between start and end time) and the
            # resources required by the task, but not on the actual task.
            claim = {'starttime': None, 'endtime': None, 'properties': [], 'status': 'tentative',
                     'resource_id': claimable_resources[res_type]['id'], 'resource_type_id': res_type}

            # RCU claim size as returned by the ResourceEstimator is actually a bit pattern (encoding which of a
            # station's RCUs are requested to take part in a measurement and which not). In order to have it countable
            # (as is expected of a claim size) it needs to be replaced with the number of RCUs requested. Subsequently,
            # the bit pattern information is stored with the claim separately
            if res_type == self.resource_types['rcu']:
                used_rcus = needed_resources[self.resource_types['rcu']]
                claim_size = used_rcus.count('1')
                claim['used_rcus'] = used_rcus
            else:
                claim['used_rcus'] = None

            claim['claim_size'] = claim_size

            claims.append(claim)

        return claims

    def _reduce_resource_availability(self, claimable_resources_dict, claims):
        """ Reduce the resource_availability for the resources in claimable_resources_dict
            with the sizes of the given claims. """

        for claim in claims:
            resource_type_id = claim['resource_type_id']
            claim_size = claim['claim_size']

            claimable_resources_dict[resource_type_id]['available_capacity'] -= claim_size
            claimable_resources_dict[resource_type_id]['claimable_capacity'] -= claim_size

    def _get_files_properties(self, files_dict, io_type):
        """ Return list of properties in claim format converted from files_dict.
            E.g. files_dict: {'cs': [ {'sap_nr': 2, ..., 'properties': {'nr_of_uv_files': 123, ...}}, {...} ], 'is': ...}
        """
        if files_dict is None:
            return []

        logger.info('_get_files_properties: processing %s_files: %s', io_type, files_dict)
        properties = []

        for dptype in files_dict:
            for dptype_dict in files_dict[dptype]:
                sap_nr = dptype_dict.get('sap_nr')  # only with obs output and obs successor input

                for prop_type_name, prop_value in list(dptype_dict['properties'].items()):
                    rc_property_type_id = self.resource_claim_property_types.get(prop_type_name)
                    if rc_property_type_id is None:
                        logger.error('getFilesProperties: ignoring unknown prop type: %s', prop_type_name)
                        continue

                    prop = {'type': rc_property_type_id, 'value': prop_value, 'io_type': io_type}
                    if sap_nr is not None:
                        prop['sap_nr'] = sap_nr
                    properties.append(prop)

        return properties

    # TODO: (Ruud B) check and decide if we need to be able to merge claims based on claim[used_rcus]
    def _merge_claims(self, claims):
        """ Merge claims allocated onto the same resources.
            To merge claim properties, summablePropTypeIds is used.
        """
        logger.info('mergeClaims: merging claims for the same resource across %d claims', len(claims))

        claims.sort( key=lambda claim: claim['resource_id'] )

        i = 1
        while i < len(claims):  # careful iterating while modifying
            if claims[i-1]['resource_id'] == claims[i]['resource_id']:
                # Merge claim_size and props: "claims[i-1] += claims[i]"
                #
                # starttime and endtime are always equal for the same resource_id
                claims[i-1]['claim_size'] += claims[i]['claim_size']
                claims[i-1]['requested_resources'].extend(claims[i]['requested_resources'])

                if 'properties' in claims[i] and len(claims[i]['properties']):
                    if 'properties' not in claims[i-1]:
                        claims[i-1]['properties'] = []
                    else:  # shallow copy to avoid aliasing; mergeResourceProperties() does the rest
                        claims[i-1]['properties'] = list(claims[i-1]['properties'])
                    self._merge_resource_properties(claims[i - 1]['properties'], claims[i]['properties'])

                claims.pop(i)  # can be more efficient O()-wise
            else:
                i += 1

    def _merge_resource_properties(self, props0, props1):
        """ Ensure props0 contains all properties of props1.
            A property of type in summablePropTypeIds must have its value added.
            NOTE: caller has to ensure that 'not (props0 is props1)' holds.
        """
        # Better datastructs could easily avoid this O(N^2). len(props) is ~5
        props0len = len(props0)
        for p1 in props1:
            found = False
            i = 0
            while i < props0len:  # careful iterating while modifying
                p0 = props0[i]
                if p0['type']       == p1['type'] and \
                   p0.get('sap_nr') == p1.get('sap_nr') and \
                   p0['io_type']    == p1['io_type']:
                    if p0['type'] in self._summable_property_type_ids():  # same and need to sum values
                        props0[i] = dict(props0[i])  # copy to avoid changing p1 too if refers to same obj
                        props0[i]['value'] += p1['value']
                    elif p0['value'] != p1['value']:
                        logger.warn('mergeResourceProperties: unexpected same prop pair, but with different values: %s and %s', p0, p1)
                    found = True
                    break
                i += 1

            if not found:
                props0.append(p1)
