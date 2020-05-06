#!/usr/bin/env python3
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id$

"""
resourcetool.py

Simple utility to list or update RADB resource availability values.
Essentially a tool around RADB getResources(), updateResourceAvailability(), getResourceClaims() and (parts of) updateResourceClaims().

Can also figure out available capacity for a mounted storage resource and update it in the RADB (-U/--update-available-storage-capacity option).
Can also update storage claim endtime to its task endtime (if ended) in the RADB (-E/--end-past-tasks-storage-claims option).
Examples (source lofarinit.sh to set LOFARROOT, PYTHONPATH, ...):
- Update available (local) storage capacity and set storage claim endtimes to task endtimes (if ended) for an observation storage node, e.g. via cron in operations:
    source /opt/lofar/lofarinit.sh; LOFARENV=PRODUCTION /opt/lofar/bin/resourcetool --broker=scu001.control.lofar --end-past-tasks-storage-claims --update-available-storage-capacity
- Show all DRAGNET resources on the test system RADB:
    LOFARENV=TEST resourcetool --broker=scu199.control.lofar --resource-group-root=DRAGNET
- Deactivate 2 storage resources in operations, because disks from both storage areas are found to be faulty (then still need to re-schedule tasks):
    LOFARENV=PRODUCTION resourcetool --broker=scu001.control.lofar drg01_storage:/data1=False drg01_storage:/data2=False

NOTES:
! Be careful what system (operations or test) this command applies to! This can be set using the env vars LOFARENV=TEST or LOFARENV=PRODUCTION
  Operations vs Test (vs Development) can be seen from the default RADB_BUSNAME in the usage info: lofar.* vs test.lofar.* vs devel.lofar.*
! By default, listed or updateable resources are restricted to resources under the localhost's resource group.
  This is on purpose to make -U work correctly. The -G/--resource-group-root option can be used to widen the resource group scope for listing
  or explicit command-line updates, but non-default -G with -U is rejected: it is too easy to mass-update other resources with local filesystem info.
"""

import logging
from datetime import datetime, timedelta

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.common.util import humanreadablesize

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)

def printResources(resources, scaled_units=True):
    """ E.g.: resources = [{u'total_capacity': 3774873600, u'name': u'dragproc_bandwidth:/data', u'type_id': 3,
                            u'available_capacity': 3774873600, u'type_name': u'bandwidth', u'unit_id': 3,
                            u'active': True, u'used_capacity': 0, u'id': 118, u'unit': u'bits/second',
                            'claimable_capacity': 3774873600}, ...]  # this key was added (not from RADB); it can be negative!
    """
    header = {'id': 'RId', 'name': 'Resource Name', 'active': 'Active',
              'available_capacity': ' Avail. Capacity', 'claimable_capacity': '  Claimable Cap.',
              'total_capacity': '  Total Capacity', 'unit': 'Unit'}
    print(('{id:4s} {name:24s} {active:6s} {available_capacity} {claimable_capacity} {total_capacity} {unit}'.format(**header)))
    print('===================================================================================================')
    resources.sort(key=lambda r: r['id'])  # SQL could have done this better
    for res in resources:
        res['active'] = 'True' if res['active'] else 'False'  # to solve bool formatting issue

        if scaled_units and (res['type_name'] == 'storage' or res['type_name'] == 'bandwidth'):
            unit_base = 1024 if res['type_name'] == 'storage' else 1000  # check type_name instead of unit as in printClaims()
            res['available_capacity'] = humanreadablesize(res['available_capacity'], '', unit_base)
            res['claimable_capacity'] = humanreadablesize(res['claimable_capacity'], '', unit_base)
            res['total_capacity']     = humanreadablesize(res['total_capacity']    , '', unit_base)
            cap_conv = '>16s'
        else:
            cap_conv = '16d'

        print((('{id:4d} {name:24s} {active:6s} {available_capacity:' + cap_conv +
               '} {claimable_capacity:' + cap_conv + '} {total_capacity:' + cap_conv + '} {unit}').format(**res)))
    if not resources:
        print('<no resources>')

def printClaims(claims, scaled_units=True):
    """ E.g.: claims = [{u'claim_size': 76441190400, u'endtime': datetime.datetime(2018, 6, 13, 17, 40),
                         u'id': 67420, u'resource_id': 122, u'resource_name': u'drg01_storage:/data1',
                         u'resource_type_id': 5, u'resource_type_name': u'storage',
                         u'starttime': datetime.datetime(2017, 6, 13, 17, 30),
                         u'status': u'claimed', u'status_id': 1, u'task_id': 75409, ...}, ...]
    """
    header = {'id': 'ClId', 'resource_name': 'Resource Name', 'starttime': 'Start Time', 'endtime': 'End Time',
              'claim_size': 'Claim Size', 'status': 'Status'}
    print(('{id:7s} {resource_name:24s} {starttime:19s} {endtime:19s} {claim_size:16s} {status:8s}'.format(**header)))
    print('===================================================================================================')
    claims.sort(key=lambda c: c['id'])         # secondary sorting key; SQL could have done this better
    claims.sort(key=lambda c: c['starttime'])  # primary sorting key (stable sort)
    for claim in claims:
        if scaled_units and (claim['resource_type_name'] == 'storage' or claim['resource_type_name'] == 'bandwidth'):
            unit_base = 1024 if claim['resource_type_name'] == 'storage' else 1000  # no unit name here, so check type_name
            claim['claim_size'] = humanreadablesize(claim['claim_size'], '', unit_base)
            size_conv = '>16s'
        else:
            size_conv = '16d'

        print((('{id:7d} {resource_name:24s} {starttime} {endtime} {claim_size:' + size_conv +
               '} {status:8s}').format(**claim)))
    if not claims:
        print('<no claims on specified resources and time range>')

def updateStorageClaimsEndTime(radb, resources, storage_resource_type_id, lower_bound=None, upper_bound=None):
    """ Update storage claims on resources in the RADB that currently apply, but the task
        they belong to has ended (+ a short while). Set end time of these claims to task endtime.

        This is intended for user clusters (e.g. DRAGNET) that do not auto-terminate storage claims on
        cleanup. If users manage clean up autonomously, then they manage all storage accounting themselves.
    """
    status = 0

    resource_ids = [res['id'] for res in resources]
    now = datetime.utcnow()
    if lower_bound is None:
        lower_bound = now
    if upper_bound is None:
        upper_bound = now

    claims = radb.getResourceClaims(lower_bound=lower_bound, upper_bound=upper_bound,
                                    resource_ids=resource_ids,
                                    resource_type=storage_resource_type_id)

    # Get associated tasks for their end times. Update claims for tasks that ended.
    task_ids = list(set({claim['task_id'] for claim in claims}))
    tasks = radb.getTasks(task_ids=task_ids)
    for task in tasks:
        # Wait until task ended. Do not race with OTDBtoRATaskStatusPropagator that extends storage claim endtime.
        # We effectively undo that extension here. Intended for clusters (e.g. DRAGNET) where end users manage storage.
        new_endtime = task['endtime']
        if now < new_endtime + timedelta(minutes=1):
            continue

        claim_ids = [claim['id'] for claim in claims if claim['task_id'] == task['id'] and \
                                                        claim['endtime'] > new_endtime]
        print(("Updating RADB storage claims {} endtime to {}".format(claim_ids, new_endtime)))
        updated_dict = radb.updateResourceClaims(where_resource_claim_ids=claim_ids, endtime=new_endtime)
        if not updated_dict['updated']:
            logger.error('failed to update RADB storage claims')  # why is N/A here; check the RA logs
            status = 1

    return status

def updateResource(radb, resource):
    """ Update the RADB using the resource dict. """
    print(("Updating RADB with resource {}".format(resource)))
    updated_dict = radb.updateResourceAvailability(resource_id=resource['id'], active=resource['active'],
                                                   available_capacity=resource['available_capacity'],
                                                   total_capacity=resource['total_capacity'])
    if not updated_dict['updated']:
        logger.error('failed to update RADB resource')  # why is N/A here; check the RA logs
        return 1
    return 0

def getMountPoint(resource_name):
    """ E.g. with resource_name 'CEP4_storage:/data' or 'drg15_bandwidth:/data2' or 'CS002bw0',
        this function returns: '/data' or '/data2' or None.
    """
    sep_idx = resource_name.find(':/')  # mount point must be an abs path
    if sep_idx == -1:
        return None
    return resource_name[sep_idx + 1 : ]

def updateAvailableStorageCapacities(radb, resources):
    import os
    status = 0

    for res in resources:
        # All storage resource names are supposedly mount points.
        # But do not update with the wrong partition info (sys maintenance?).
        # Log error and let admin figure it out. RADB resource defaults may need updating too.
        mount_pt = getMountPoint(res['name'])
        if mount_pt is None or not os.path.ismount(mount_pt):
            logger.error("skipped updating available capacity of resource '{}': its path is not a mount point on this system".format(res['name']))
            status = 1
            continue

        # Retrieve avail capacity from filesystem and do some checks.
        try:
            st = os.statvfs(mount_pt)
        except OSError as e:
            logger.error('statvfs: ' + str(e))
            status = 1
            continue
        avail_cap = st.f_bavail * st.f_frsize
        total_cap = st.f_blocks * st.f_frsize
        if total_cap != res['total_capacity']:
            hint_arg = res['name'] + '=' + str(avail_cap) + ',' + str(total_cap)
            logger.warn("total capacity for resource '{}' is {}, which is not equal to {} as listed in the RADB. If the total capacity has changed permanently, please update the RADB, e.g. by running this program passing: {} (and by updating the software repo for RADB reinstalls).".format(res['name'], total_cap, res['total_capacity'], hint_arg))
        if avail_cap > res['total_capacity']:
            logger.error("the detected available capacity for resource '{}' cannot be written to the RADB, because it is greater than the total capacity listed in the RADB.")
            status = 1
            continue

        # Only update available capacity in the RADB.
        # Total and active indicate a config change (or maintenance in progress). Leave that for an admin.
        res_update = {'id': res['id'], 'available_capacity': avail_cap,
                      'total_capacity': None, 'active': None}
        status |= updateResource(radb, res_update)

    return status

def updateSpecifiedCapacities(radb, resources, resource_updates):
    status = 0

    for res_update in resource_updates:
        # Need resource id from name to apply the update. Also check avail <= total.
        try:
            res = next((res for res in resources if res['name'] == res_update['name']))
        except StopIteration:
            logger.error("skipped updating resource '{}': name unknown. Correct the name or (correct the) use (of) the -G/--resource-group-root option to widen the resource scope, e.g. -G CEP4|DRAGNET|LOFAR".format(res_update['name']))
            status = 1
            continue

        if res_update['available_capacity'] is not None and \
           res_update['total_capacity'] is None and \
           res_update['available_capacity'] > res['total_capacity']:
            logger.error("skipped updating resource '{}': specified available capacity cannot be greater than total capacity listed in the RADB. If the total capacity has changed permanently, please update the RADB using this program (and by updating the software repo for RADB reinstalls)".format(res_update['name']))
            status = 1
            continue

        res_update['id'] = res['id']
        status |= updateResource(radb, res_update)

    return status

def getResourceGroupIdByName(db_rgp2rgp, name):
    """ Returns group id of resource group named name, or None if name was not found.
        The search happens breadth-first.
    """
    # find root group(s): empty parent list
    gids = [gid for gid, group in list(db_rgp2rgp.items()) if not group['parent_ids']]

    i = 0
    while i < len(gids):  # careful iterating while modifying
        res_group = db_rgp2rgp[gids[i]]
        if res_group['resource_group_name'] == name:
            return gids[i]
        gids.extend(res_group['child_ids'])
        i += 1

    return None

def getSubtreeResourceIdList(db_rgp2rgp, root_gid):
    """ Returns list of resource ids in resource group root_gid and its (grand)children."""
    # Search breadth-first starting at root_gid.
    gids = [root_gid]
    resource_id_list = []

    i = 0
    while i < len(gids):  # careful iterating while modifying
        res_group = db_rgp2rgp[gids[i]]
        resource_id_list.extend(res_group['resource_ids'])
        gids.extend(res_group['child_ids'])
        i += 1

    return resource_id_list

def parseResourceArg(arg):
    """ Return dict parsed from arg str. Arg format: resource_name:/data=True,100,200
        with any value optional after the '=' (but need at least one).
        Any returned dict value but the resource name may be None.
        On error ValueError is raised.
    """
    eq_idx = arg.find('=')
    if eq_idx == -1:
        raise ValueError("could not find '=' in argument; need e.g. res_name=100 or resource_name=True,100,200")

    resource_name = arg[ : eq_idx]
    if not resource_name:
        raise ValueError("invalid resource name in argument before '='; need e.g. res_name=100 or resource_name=True,100,200")
    resource_val = arg[eq_idx + 1 : ]
    vals = resource_val.split(',')
    if not vals or len(vals) > 3:
        raise ValueError("need 1-3 argument value(s) after '=', e.g. res_name=100 or resource_name=True,100,200")

    active = None
    avail_cap = None
    total_cap = None
    for val in vals:
        if val == 'True' or val == 'False':
            if active is not None:
                raise ValueError("accepting at most 1 bool as resource active value in argument")
            active = True if val == 'True' else False
            continue

        if total_cap is not None:
            raise ValueError("accepting at most 2 ints as resource available and total capacities in argument")
        v = int(val)
        if v < 0:
            raise ValueError("capacity value must be positive")
        if avail_cap is None:
            avail_cap = v
        else:
            if v < avail_cap:
                raise ValueError("specified available capacity cannot be greater than specified total capacity")
            total_cap = v

    return {'name': resource_name, 'active': active,
            'available_capacity': avail_cap, 'total_capacity': total_cap}

def parseTimestamps(datetime_fmt, timestamps):
    """ Return list of None or datetime objects representing timestamps. Raise ValueError on parse error.
        Use datetime_fmt as the strptime() format str. A timestamp value may also be 'now' (UTC) or 'None'.
    """
    # Parsing datetime strings could be done by extending optparse's Option class, but this works well enough
    rv = []
    now = None

    for ts in timestamps:
        if ts is None or ts == 'now':
            if now is None:
                now = datetime.utcnow()
            ts = now
        elif ts == 'None':
            ts = None
        else:
            ts = datetime.strptime(ts, datetime_fmt)
        rv.append(ts)

    return rv

def parseArgs(args):
    from socket import gethostname 
    hostname = gethostname()

    from optparse import OptionParser
    usage = 'Usage: %prog [OPTIONS] [resource_name=available_capacity]... or [resource_name=True|False[,avail_cap[,total_cap]]]...'
    descr = 'List or update LOFAR RADB resource availability and/or available/total capacities'
    parser = OptionParser(usage=usage, description=descr)
    # already supported options: -h, --help, --
    parser.add_option('-q', '--broker', dest='broker', default=DEFAULT_BROKER,
                      help='qpid broker hostname (default: %default).')
    parser.add_option('--busname', dest='busname', default=DEFAULT_BUSNAME,
                      help='Name of the bus for all messaging operations (default: %default)')
    parser.add_option('-G', '--resource-group-root', dest='resource_group_root', default=hostname,
                      help='Only consider resources under resource group root (default: this hostname: \'%default\' (all=LOFAR))')
    parser.add_option('-t', '--resource-type', dest='resource_type', default=None,
                      help='Only consider resources of this type (e.g. storage, bandwidth, rsp, rcu, ...)')
    parser.add_option('-E', '--end-past-tasks-storage-claims', dest='end_storage_claims', action='store_true', default=False,
                      help='WARNING: USE THIS OPTION ONLY FOR DRAGNET!. Set end time to task stoptime for storage claims under --resource-group-root for completed tasks. Implies -t storage. Can be limited to timerange given by -T and -S.')
    parser.add_option('-U', '--update-available-storage-capacity', dest='update_avail', action='store_true', default=False,
                      help='Update the available capacity value in the RADB of storage resources under --resource-group-root. Implies -t storage. Not affected by -T and -S.')
    datetime_fmt = '%Y-%m-%d %H:%M:%S'
    parser.add_option('-T', '--timestart', dest='timestart',
                      help='lower bound UTC timestamp \'{}\' or \'now\' or \'None\' for resource claims (default: now)'.format(datetime_fmt))
    parser.add_option('-S', '--timestop', dest='timestop',
                      help='upper bound UTC timestamp \'{}\' or \'now\' or \'None\' for resource claims (default: now)'.format(datetime_fmt))
    parser.add_option('--no-scaled-units', dest='no_scaled_units', action='store_true', default=False,
                      help='Print raw instead of scaled units for some sizes, e.g. 1048576 instead of 1M')
    options, left_over_args = parser.parse_args(args)

    if options.update_avail and options.resource_group_root != hostname:
        parser.error("combining the option -U with a non-default -G is rejected: it is too easy to mass-update the wrong resources")

    if options.end_storage_claims or options.update_avail:
        if options.resource_type is None:
            options.resource_type = 'storage'
        elif options.resource_type != 'storage':
            parser.error("the options -E or -U cannot be combined with -t {}, because -E and -U are about storage only".format(options.resource_type))

    try:
        timestamps = parseTimestamps(datetime_fmt, (options.timestart, options.timestop))
    except ValueError as exc:
        parser.error("timestamp arguments: " + str(exc))
    options.timestart = timestamps[0]
    options.timestop  = timestamps[1]
    if options.timestart is not None and options.timestop is not None and options.timestart > options.timestop:
        parser.error("-T/--timestart option value may not be after -S/--timestop option value")

    resource_updates = []
    for i, arg in enumerate(left_over_args):
        try:
            resource_updates.append(parseResourceArg(arg))
        except ValueError as exc:
            parser.error("failed to parse non-option argument '{}': {}".format(i, exc))

    return options, resource_updates, parser.print_help

def main(args):
    import os
    os.environ['TZ'] = 'UTC'  # LOFAR observatory software uses UTC

    options, resource_updates, print_help_func = parseArgs(args)

    status = 0
    radb = None
    try:
        radb = RADBRPC.create(exchange=options.busname, broker=options.broker)

        db_resource_list = radb.getResources(resource_types=options.resource_type, include_availability=True)

        if options.timestart is None:
            options.timestart = datetime(1970, 1, 1)
        if options.timestop is None:
            options.timestop = datetime(2100, 1, 1)

        # Filter resource list via resource root group option
        db_resource_group_mships = radb.getResourceGroupMemberships()
        db_rgp2rgp = db_resource_group_mships['groups']  # resource-group-to-resource-group relations
        group_id = getResourceGroupIdByName(db_rgp2rgp, options.resource_group_root)
        if group_id is None:
            print_help_func()
            print("")
            logger.error("could not find resource group '{}'. You may want to (correct the) use (of) the -G/--resource-group-root option to widen the resource scope, e.g. -G CEP4|DRAGNET|LOFAR".format(options.resource_group_root))
            return 1
        resource_id_list = getSubtreeResourceIdList(db_rgp2rgp, group_id)
        if not resource_id_list:
            print_help_func()
            print("")
            logger.error("no resources found under resource group '{}' and its (grand)children".format(options.resource_group_root))
            return 1
        resources = [res for res in db_resource_list if res['id'] in resource_id_list]  # SQL could have done this better

        if options.end_storage_claims:
            try:
                storage_resource_type_id = next((res['type_id'] for res in resources))
            except StopIteration:
                print_help_func()
                print("")
                logger.error("-E/--end-past-tasks-storage-claims used, but no storage resources found under resource group '{}' and its (grand)children".format(options.resource_group_root))
                return 1

            status |= updateStorageClaimsEndTime(radb, resources, storage_resource_type_id, lower_bound=options.timestart, upper_bound=options.timestop)

        if options.update_avail:
            status |= updateAvailableStorageCapacities(radb, resources)

        if resource_updates:
            status |= updateSpecifiedCapacities(radb, resources, resource_updates)

        # If no specific action requested, print list of resources and claims
        if not options.end_storage_claims and not options.update_avail and not resource_updates:
            resource_ids = [res['id'] for res in resources]
            claims = radb.getResourceClaims(lower_bound=options.timestart, upper_bound=options.timestop,
                                            resource_ids=resource_ids, extended=True)

            # A small downside of querying RADB again is that the claimable capacities might be inconsistent with claims just retrieved.
            # We could derive it ourselves or stick it in a transaction, but this is good enough for the overview.
            for res in resources:
                res['claimable_capacity'] = radb.get_resource_claimable_capacity(resource_id=res['id'],
                                                                                 lower_bound=options.timestart,
                                                                                 upper_bound=options.timestop)

            printResources(resources, not options.no_scaled_units)
            print("")
            printClaims(claims, not options.no_scaled_units)

    #except Exception:  # disabled: prefer default stacktrace on bug here
    finally:
        if radb is not None:
            radb.close()

    return status

if __name__ == '__main__':
    from sys import argv, exit
    exit(main(argv[1:]))

