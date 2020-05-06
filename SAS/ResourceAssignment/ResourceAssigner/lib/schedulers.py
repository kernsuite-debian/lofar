from datetime import datetime, timedelta
from copy import deepcopy

from lofar.common.cache import cache
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

from lofar.sas.resourceassignment.database.radb import RADatabase, PostgresDBQueryExecutionError

from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

from lofar.sas.resourceassignment.resourceassigner.resource_availability_checker import CouldNotFindClaimException

from lofar.sas.resourceassignment.common.specification import Specification

import logging
from functools import reduce
logger = logging.getLogger(__name__)


""" Scheduling is the process of looking for a suitable resource slot for a given task.

    The following code allows three levels of scheduling:

    * The /BasicScheduler/ locates resources for a task between its specified start- and endtime.
    * The /StationScheduler/ resolves station requirements (">=5 core stations") into a station list.
    * The /PriorityScheduler/ enhances the BasicScheduler, and kills lower-priority tasks to make room for the given 
      task.
    * The /DwellScheduler/ enhances the PriorityScheduler, by increasing the starttime until the task can be scheduled.

    Each level contains hooks to support the next.

    All schedulers modify the database directly, and commit() if a solution if found. If not, a rollback()
    is performed. To use:

        sched = <schedulerclass>(...)
        (success, changed_tasks) = sched.allocate_resources()
    changed_tasks can be a list of changed tasks that will need to be communicated to OTDB and such   
"""


class ScheduleException(Exception):
    """ Scheduler related exceptions should distinctive from general Exceptions """

    def __init__(self, message):
        super(ScheduleException, self).__init__(message)

class BasicScheduler(object):
    """ A Scheduler that allocates resources at a fixed time. Resources are searched for. """

    def __init__(self, task_id, specification_tree, resource_estimator, resource_availability_checker, radb: RADatabase):
        """
        Creates a BasicScheduler instance

        :param task_id: the ID of the task to be scheduled
        :param specification_tree: the full specification; will be modified where needed with respect to resources
        :param resource_estimator: the ResourceEstimator function that turns a specification into resource estimates
        :param resource_availability_checker: the ResourceAvailabilityScheduler to be used by the BasicScheduler
        :param radb: a RADatabase instance.

        :raises AssertionError if task_id is a negative number or is None
        """

        self.task_id = task_id
        self.specification_tree = specification_tree
        self.resource_estimator = resource_estimator
        self.resource_availability_checker = resource_availability_checker
        self.radb = radb

        # Ensure a valid task_id is given, since radb.getTasks() will not raise if task_id equals None
        if task_id < 0:
            raise ValueError('BasicScheduler, task_id=%s should be >= 0', task_id)

        # Cache our task info
        self.task = self.radb.getTask(id=task_id)
        self.starttime = self.task["starttime"]
        self.endtime = self.task["endtime"]

        # Any resources that we cannot schedule on for some reason
        self.unusable_resources = []

        # Duration must be positive or weird stuff will happen
        if self.starttime >= self.endtime:
            raise ValueError('BasicScheduler, starttime=%s should be >= endtime=%s', self.starttime, self.endtime)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        pass

    def close(self):
        pass

    def allocate_resources(self):
        """
        Tries to allocate resources for the given estimates.

        :returns: True if allocation was successful or False if not
        :returns: changed_tasks: tasks that had their status changed as a result of the task scheduling
        """
        # any resources we cannot schedule on, either because we've already
        # tried, or because there's already a claim of us there

        allocation_successful = False
        changed_tasks = [] #Not used in the BasicScheduler, but in derived schedulers it is

        try:
            # pre process
            self._pre_process_allocation()

            # fetch what is available
            available_resources = self._get_resource_availability()

            # perform the actual scheduling
            self._schedule_task(available_resources)

            # post process
            changed_tasks = self._post_process_allocation()

            # Make changes effective
            self.radb.commit()

            allocation_successful = True
        except ScheduleException as e:
            logger.exception("%s: scheduling threw ScheduleException: %s", self.__class__.__name__, e)
            self._handle_schedule_exception()
        except Exception as e:
            logger.exception("%s: scheduling threw unhandled exception: %s", self.__class__.__name__, e)
            raise

        return (allocation_successful, changed_tasks)

    def _handle_schedule_exception(self):
        """
        The BasicScheduler does not care about ScheduleException's, no rollback is needed or wanted.
        We just want everything in the radb, and let the user decide how to act.
        """
        logger.info("BasicScheduler: ignoring ScheduleException, accepting current solution into radb")
        self.radb.commit()

    def _pre_process_allocation(self):
        """
        Cleans unusable resources so that on a next try thet will not block based on previous usage.
        """
        self.unusable_resources = []

        logger.debug("BasicScheduler: _pre_process_allocation for task %s", self.task_id)

    def _post_process_allocation(self):
        """
        Placeholder for derived classes, available to be able perform any processing after the actual allocation of
        resources done by allocate_resources().

        If not overridden, or at least called by the derived class(es), tries to move all claims from "tentative" to a
        "claimed" status.

        :raises ScheduleException if the task at hand can't be set to the status "claimed" in RADB
        """

        logger.debug("BasicScheduler: _post_process_allocation for task %s", self.task_id)

        # move all claims from tentative -> claimed
        try:
            if not self.radb.updateResourceClaims(where_task_ids=[self.task_id], status="claimed", commit=False):
                raise ScheduleException("Failed to put tentative claims to claimed")
        except PostgresDBQueryExecutionError as e:
            raise ScheduleException("Failed to put tentative claims to claimed. error: %s" % (e,))

        changed_tasks = [] #Not used in the BasicScheduler, but in derived schedulers it is
        return changed_tasks

    def _get_resource_availability(self):
        """
        Get the resources available for scheduling.
        """

        return self.radb.getResources(include_availability=True, claimable_capacity_lower_bound=self.starttime,
                                      claimable_capacity_upper_bound=self.endtime)

    def _allowed_resources(self, resources):
        """ Return only the resources we're allowed to use for further claims. """

        # resources WE claimed (note that their size is already accounted for in 'resources')
        tentative_claims = self.radb.getResourceClaims(task_ids=[self.task_id], status="tentative", extended=True)
        tentative_resources = [c["resource_id"] for c in tentative_claims]

        # disable resources we cannot schedule on (we cannot schedule on resources with tentative
        # claims until we implement merging tentative claims)
        disabled_resources = self.unusable_resources + tentative_resources

        # disable resources for various reasons
        return [r for r in resources if r["id"] not in disabled_resources]

    def _finalise_claims(self, claims):
        """
        Finalize the given claims

        :param claims: the claims to finalize
        """

        for c in claims:
            c["status"] = "tentative"  # we MUST insert as "tentative", as radb demands so
            c["starttime"] = self.starttime
            c["endtime"] = self.endtime

    def _get_estimates(self):
        """ Return the estimates for a given specification. """

        return self.resource_estimator(self.specification_tree)

    def _schedule_task(self, available_resources):
        """ Schedule all required resources into the available resources. """

        # Determine new estimations based on the new station list
        estimates = self.resource_estimator(self.specification_tree)

        # Schedule them
        self._schedule_resources(estimates, available_resources, need_all=True)

    def _schedule_resources(self, requested_resources, available_resources, need_all=True):
        """ Schedule the requested resources into the available ones. Return the remaining list
            of unschedulable resources (if need_all=False, otherwise return []). """

        while requested_resources:
            try:
                remaining = self._try_schedule_resources(requested_resources, available_resources, need_all)
            except ScheduleException as e:
                # Cannot schedule any resource nor resolve any conflict
                if need_all:
                    raise
                else:
                    return requested_resources

            requested_resources = remaining

        return []

    def _try_schedule_resources(self, requested_resources, available_resources, need_all=True):
        """
        Schedule the estimates within the available resources.

        :param requested_resources: the requested resources to schedule
        :returns the set of estimates that could not be scheduled.
        :raises ScheduleException if it could not schedule the resources due to conflicts
        """

        try:
            logger.debug("Requested resources: %s", requested_resources)
            logger.debug("Available resources: %s", available_resources)

            assert requested_resources

            # strip any resources we're not allowed to use
            allowed_resources = self._allowed_resources(available_resources)

            try:
                tentative_claims = self.resource_availability_checker.get_is_claimable(requested_resources,
                                                                                       allowed_resources)
                logger.debug("Proposing tentative claims: %s", tentative_claims)
            except CouldNotFindClaimException as e:
                logger.exception('_try_schedule_resources CouldNotFindClaimException: %s', e)
                raise ScheduleException("Could not schedule: %s" % str(e))

            assert tentative_claims

            # add static info to all claims
            self._finalise_claims(tentative_claims)

            # insert all claims to reserve the resources in the next call to findfit and to find the conflicts according to
            # the DB
            claim_ids = self.radb.insertResourceClaims(self.task_id, tentative_claims, 'anonymous', -1, commit=False)
            logger.debug("Resulting claim IDs: %s", claim_ids)
            assert len(claim_ids) == len(tentative_claims), "Could not insert resource claims"

            # tie the claim ids to the estimates. note that each "requested_resources" element is a list of claims
            claim_to_estimates = {cid: tentative_claims[idx]["requested_resources"] for idx, cid in enumerate(claim_ids)}

            # try solving as much conflicts as possible. We need NOT resolve ALL conflicts: removing one conflict can free
            # up more resources as a by-product, in which case other conflicts can simply be shifted to those newly freed
            # resources.
            conflict_claims = self.radb.getResourceClaims(task_ids=[self.task_id], status="conflict", extended=True)
            logger.info("Resulting claims in conflict before resolution: %s", conflict_claims)

            if conflict_claims and not any([self._resolve_conflict(c) for c in conflict_claims]):
                if need_all or len(conflict_claims) == len(tentative_claims):
                    # Could not resolve any conflict
                    raise ScheduleException("Could not resolve one or more conflicting claims: #tentative_claims=%s #conflict_claims=%s conflict_claims=%s" % (
                                            len(tentative_claims), len(conflict_claims), conflict_claims))

            # remove conflicting claims (allowing the next iteration to propose alternatives). Note that _handle_conflicts
            # could have reduced the number of conflicting claims.
            conflict_claims = self.radb.getResourceClaims(task_ids=[self.task_id], status="conflict", extended=True)
            logger.info("Resulting claims in conflict after resolution: %s", conflict_claims)

            conflict_claim_ids = [c["id"] for c in conflict_claims]
            self.radb.deleteResourceClaims(conflict_claim_ids, commit=False)

            # return any estimates that we could not fulfill. Note that requested_resources can contain the same item multiple
            # times, so remove only the same number of estimates that were satisfied
            satisfied_estimates = sum([claim_to_estimates[cid] for cid in claim_to_estimates if cid not in conflict_claim_ids], [])
            remaining_estimates = requested_resources[:]
            for e in satisfied_estimates:
                if e in remaining_estimates:
                    remaining_estimates.remove(e)

            logger.info("Remaining estimates: %s", remaining_estimates)
            return remaining_estimates
        except PostgresDBQueryExecutionError as e:
            raise ScheduleException("Error while scheduling resources: %s" % (e,))

    def _resolve_conflict(self, conflict_claim):
        """ Resolve one conflict, making it is useful to try to schedule again.

            :returns True if the conflict might have been resolved.
            :returns False if nothing can be done.
        """

        return False

class StationScheduler(BasicScheduler):
    """ A scheduler that honours station requirements (root_resource_group, minimum) pairs, trying
        to find the largest set of stations fulfilling the requirements. If an observation has a fixed
        station list already, no special action is taken. 
        
        After scheduling, the get_stations() function returns a list of the allocated stations. """

    def __init__(self, task_id, specification_tree, resource_estimator, resource_availability_checker,
                 radb: RADatabase,
                 broker=DEFAULT_BROKER):
        """
        Creates a StationScheduler instance

        :param task_id: the ID of the task at hand
        :param specification_tree: the full specification; will be modified where needed with respect to resources
        :param resource_estimator: the ResourceEstimator function that turns a specification into resource estimates
        :param resource_availability_checker: the ResourceAvailabilityChecker instance to use
        :param radb: a RADatabase instance. 
        :param mom_busname: the MoM Query service bus name (default: 'lofar.ra.command')
        :param mom_servicename: the MoM Query service name (default: 'momqueryservice')
        :param broker: the message broker to use for send messages/RPC calls/etc.
        """

        super(StationScheduler, self).__init__(task_id, specification_tree, resource_estimator, resource_availability_checker, radb)

        # For observations without a fixed station list, we need to derive one. TODO: this likely isnt the condition we want to decide on
        self.must_derive_station_list = specification_tree["task_type"] == "observation" and specification_tree["specification"]["Observation.VirtualInstrument.stationList"] == [] and specification_tree["station_requirements"]

    def _handle_schedule_exception(self):
        """
        All derived classes of the BasicScheduler do care about ScheduleException's, and we do want to rollback.
        """
        logger.info("%s: handling ScheduleException by doing rollback of current solution", self.__class__.__name__)
        self.radb.rollback()

    @cache
    def _expand_station_list(self, resource_group):
        """ Given a resource group name, return a list of station names below it. """

        # Query the full resource group structure
        resources = self.radb.getResourceGroupMemberships()
        groups = resources["groups"]

        # collect subgroup ids recursively, start with the provided group name
        groups_to_scan = [g for g in groups.values()
                            if g["resource_group_name"] == resource_group]

        if not groups_to_scan:
            raise ScheduleException("Unknown resource group: %s" % resource_group)

        subgroup_ids = [g["resource_group_id"] for g in groups_to_scan] # start with given list, as it may already be a station
        while groups_to_scan:
            g = groups_to_scan.pop()
            subgroup_ids.extend(g["child_ids"])
            groups_to_scan.extend([groups[cid] for cid in g["child_ids"]])

        # collect child resource groups that are stations
        stations = [groups[sid]["resource_group_name"]
                        for sid in set(subgroup_ids)
                        if groups[sid]["resource_group_type"] == "station"]

        return stations

    def _get_station_estimates(self):
        """ Return the station estimates only. """

        estimates = self._get_estimates()
        return [e for e in estimates if "station" in e]

    @staticmethod
    def _requirements_satisfied_without(requirements, unclaimable):
        """ Return whether the given (station) requirements are satisfied if the given list
            cannot be claimed. 

            :param requirements         A list if (stations, minimum) pairs.
            :param unclaimables         A set of unclaimable stations.
        """

        for wanted_list, minimum in requirements:
            num_missing = len([1 for s in unclaimable if s in wanted_list])

            if len(wanted_list) - num_missing < minimum:
                logger.warning("Could not allocate %s stations out of %s (need %d stations)." % (num_missing, wanted_list, minimum))
                return False

        return True

    def _find_stations(self, available_resources):
        """ Find out which subset of the stations we can allocate that satisfy the station requirements,
            and return that station set. Rolls back the database.
            
            The strategy is:
              1) Try to allocate all stations that could fulfill a requirement.
              2) Check if enough allocations succeed to fulfill all requirements.
              3) Roll back.
              4) Throw if not all requirements could be fulfilled.
              5) Return the successfully allocated stations.
              
            The roll-back in a success scenario is a short cut currently taken to avoid having to deal
            with stations that have a partial successful allocation of resources. """

        # Station requirements are (root_resource_group, minimum) pairs

        # Construct a list of (stations, minimum) pairs we require
        expanded_requirements = [(self._expand_station_list(group), minimum) for (group, minimum) in self.specification_tree["station_requirements"]]

        # Accumulate all the stations we want from all pairs
        wanted_stations = list(reduce(set.union, [set(stations) for stations, _ in expanded_requirements], set()))

        # Convert station lists into resource requirements
        self._set_stations(wanted_stations)
        wanted_estimates = self._get_station_estimates()

        # Try to schedule all of the stations.
        # make a (deep)copy of available_resources and use that,
        # because _schedule_resources modifies the available_capacity of the tested wanted stations.
        # we rollback the radb later in this method, so we should keep the original available_resources intact.
        available_resources_copy = deepcopy(available_resources)
        remaining_estimates = self._schedule_resources(wanted_estimates, available_resources_copy, need_all=False)

        # See if our allocation meets the minimal criteria. Note that some stations may be partially allocated,
        # we do not count those as claimable.
        unclaimable_stations = set([e["station"] for e in remaining_estimates])
        if not self._requirements_satisfied_without(expanded_requirements, unclaimable_stations):
            raise ScheduleException("Could not allocate enough stations. unclaimable_stations=%s" % (unclaimable_stations,))

        allocated_stations = set([e["station"] for e in wanted_estimates if e not in remaining_estimates])

        if not allocated_stations:
            # The specification might allow a minimum of 0 stations
            raise ScheduleException("Could not allocate any stations")

        # Note that each station generates multiple estimates, which could be partially fulfilled.
        # We thus need to explicitly remove claims for stations we are not going to use.
        # For now, we just roll back and reallocate everything (stations and non stations) later on
        self.radb.rollback()

        return allocated_stations

    def _set_stations(self, stations):
        """ Update the current spec with the given station list. """
        self.specification_tree["specification"]["Observation.VirtualInstrument.stationList"] = stations

    def get_stations(self):
        """ Return the list of stations we've used for scheduling the task (if any). """
        return self.specification_tree["specification"].get("Observation.VirtualInstrument.stationList", [])

    def _schedule_task(self, available_resources):
        """ Schedule all required resources into the available resources. """

        # Determine and set the station list, if not given
        if self.must_derive_station_list:
            stations = self._find_stations(available_resources)
            self._set_stations(stations)

        # Schedule all resources
        super(StationScheduler, self)._schedule_task(available_resources)


class PriorityScheduler(StationScheduler):
    """ A Scheduler that searches for an allocation with a fixed start time, but flexible resources.
        Conflict resolution is done by killing jobs with lower priority. """

    def __init__(self, task_id, specification_tree, resource_estimator, resource_availability_checker,
                 radb: RADatabase,
                 broker=DEFAULT_BROKER):
        """
        Creates a PriorityScheduler instance

        :param task_id: the ID of the task at hand
        :param specification_tree: the full specification; will be modified where needed with respect to resources
        :param resource_estimator: the ResourceEstimator function that turns a specification into resource estimates
        :param resource_availability_checker: the ResourceAvailabilityChecker instance to use
        :param radb: a RADatabase instance. 
        :param broker: the message broker to use for send messages/RPC calls/etc.
        """

        super(PriorityScheduler, self).__init__(task_id, specification_tree, resource_estimator, resource_availability_checker, radb)

        self.momqueryservice = MoMQueryRPC.create(broker=broker, timeout=180)

        # Time needed in between tasks to setup the stations
        self.STATION_SETUP_TIME_MINUTES = 1

    def open(self):
        """ Open connections to the required services """
        super().open()
        self.momqueryservice.open()

    def close(self):
        """ Close the connections with the used services """
        super().close()
        self.momqueryservice.close()

    def _pre_process_allocation(self):
        """ Take care of actions to be taken prior to the scheduling of resources """
        super(PriorityScheduler, self)._pre_process_allocation()

        self.earliest_potential_starttime = datetime.max
        self.tasks_to_kill = []
        self.tasks_to_unschedule = []

    def _post_process_allocation(self):
        """ Take care of actions to be taken after to the scheduling of resources """
        changed_tasks = super(PriorityScheduler, self)._post_process_allocation()

        #killing and unscheduling happens in the resource assigner
        for t in (self.tasks_to_kill + self.tasks_to_unschedule):
            # _send_task_status_notification in resourceassigner expects an object (of type Specification)
            # It seems easier to create a Specification than creating a custom object/class just for this
            # and adapting the resourceassigner code
            spec = Specification(None, None, None)
            spec.radb_id = t["id"]
            spec.mom_id = t["mom_id"]
            spec.otdb_id = t["otdb_id"]
            spec.status = t["status"]
            spec.type = t["type"]
            changed_tasks.append(spec)
        return changed_tasks

    @cache
    def _my_task_priority(self):
        """
        Returns the priority of the current task

        :returns the priority of the current task
        """

        logger.debug("my_task_priority, messing around with MoM QS")

        my_momid = self.task["mom_id"]
        priority_dict = self.momqueryservice.get_project_priorities_for_objects([my_momid])
        my_priority = priority_dict[my_momid]

        logger.debug("PriorityScheduler: my priority is %s", my_priority)
        return my_priority

    def _kill_task_in_radb(self, task):
        """
        Emulate killed task by setting its endtime to utcnow() in RADB

        :param task: task to 'set' to killed
        """

        logger.debug("kill_task_in_radb: task: %s", task)

        new_endtime = max(task['starttime']+timedelta(seconds=1), datetime.utcnow()) # make sure endtime is always > starttime
        self.radb.updateTaskAndResourceClaims(task_id=task['id'], task_status='aborted',
                                              endtime=new_endtime, commit=False)

    def _unschedule_task_in_radb(self, task):
        """
        unschedule the task by setting its status to conflict in RADB
        and by releasing the task's claims (set them to tentative)

        :param task: task to 'set' to conflict

        Please note that setting to approved is not a valid move, as things like the PreScheduler act on that.
        """

        logger.info("_unschedule_task_in_radb: task: %s", task)

        self.radb.updateTaskAndResourceClaims(task_id=task['id'], task_status='conflict',
                                              claim_status='tentative', commit=False)

    def _propose_potential_starttime(self, newstarttime):
        """
        Propose a new start time at which allocation could succeed. We only collect the earliest one proposed.

        :param newstarttime: the newly proposed start time
        """

        logger.debug("PriorityScheduler: Proposing starttime %s", newstarttime)

        self.earliest_potential_starttime = min(self.earliest_potential_starttime, newstarttime)

    def _resolve_conflict(self, conflict_claim):
        """
        Try to resolve the given conflicting resource claim by killing tasks that have a lower priority than the task
        at hand.

        :param conflict_claim: the conflicting resource claim
        :return: True if conflict resolution was effective, or False if not
        """

        # try to resolve the conflict, and mark any resources unavailable if resolution fails
        tasks_to_move_out_of_the_way = self._get_resolvable_conflicting_tasks(conflict_claim)
        now = datetime.utcnow()

        for t in tasks_to_move_out_of_the_way:
            logger.info("_resolve_conflict: found task %s to move out of the way for claim in conflict: %s", t, conflict_claim)

            # kill running task, unschedule otherwise in order to move the blocking task out of the way
            if (t['starttime'] <= now and t['endtime'] >= now) or t['status'] == 'active': # should also do this on 'queued', but MAC_scheduler can't handle it
                # add it to the list to actually kill later
                self.tasks_to_kill.append(t)
                t['status'] = 'aborted'
                # and update the administration in the radb
                self._kill_task_in_radb(t)
            else:
                # add it to the list to unschedule later
                self.tasks_to_unschedule.append(t)
                t['status'] = 'conflict' # setting back to 'approved' would lead to all kinds of problems
                # move the blocking task out of the way
                self._unschedule_task_in_radb(t)

        if not tasks_to_move_out_of_the_way:
            logger.info("_resolve_conflict: no tasks to kill for conflict_claim %s", conflict_claim)

            # record which resources cannot be used anymore, because we can't kill anything on it
            self.unusable_resources.append(conflict_claim["resource_id"])

        # Return True if we killed anything
        return tasks_to_move_out_of_the_way != []

    def _get_conflicting_claims_and_tasks(self, conflict_claim):
        """
        Return all claims that are conflicting with our claim and all tasks associated with those claims.

        :param conflict_claim: our conflicting claim

        :returns 2-tuple (conflicting_claims, conflicting_tasks)
        """

        logger.debug("get_conflicting_claims_and_tasks for task ID: %s", conflict_claim["task_id"])

        conflicting_claims = self.radb.get_overlapping_claims(conflict_claim["id"])
        conflicting_task_ids = set([c["task_id"] for c in conflicting_claims])
        conflicting_tasks = self.radb.getTasks(task_ids=conflicting_task_ids)

        assert self.task_id not in conflicting_task_ids, "Task %s in conflict with itself!" % self.task_id

        return conflicting_claims, conflicting_tasks

    def _get_resolvable_conflicting_tasks(self, conflict_claim):
        """
        Return the tasks that that have resource claims which conflict with the given resource claim and have a lower
        priority than the task at hand (hence are resolvable).

        :param conflict_claim: the conflicting resource claim (will raise an exception if resource type is storage)
        :returns A list of tasks that can be killed
        :raises ScheduleException if the conflict could not be resolved because the given resource claim concerns a
                storage resource type.
        """

        if conflict_claim["resource_type_id"] == self.resource_availability_checker.resource_types['storage']:
            raise ScheduleException("Cannot resolve conflict on storage resource")

        # find all conflicting claims & which tasks they belong to
        conflicting_claims, conflicting_tasks = self._get_conflicting_claims_and_tasks(conflict_claim)
        conflicting_task_momids = [t["mom_id"] for t in conflicting_tasks if t["mom_id"] is not None]
        logger.debug("PriorityScheduler: conflicting claims are %s", conflicting_claims)
        logger.debug("PriorityScheduler: conflicting tasks are %s", conflicting_tasks)

        # check which tasks we can kill
        task_priorities = self.momqueryservice.get_project_priorities_for_objects(conflicting_task_momids)
        logger.debug("PriorityScheduler: conflicting task priorities are %s", task_priorities)
        # We can't kill tasks without a mom_id (reservations and such) !
        kill_task_list = [t for t in conflicting_tasks if t["mom_id"] is not None and task_priorities[t["mom_id"]] < self._my_task_priority()]
        logger.debug("PriorityScheduler: task kill list is %s", kill_task_list)

        # update if we're blocked by an earlier task than we know so far
        unkillable_task_ids = [t["id"] for t in conflicting_tasks if t not in kill_task_list]
        logger.debug("PriorityScheduler: unkillable task kill list is %s", unkillable_task_ids)
        if unkillable_task_ids:
            # note that we need to use the endtime of the claims, as they may extend beyond the task
            earliest_potential_starttime = min([c["endtime"] for c in conflicting_claims if c["task_id"] in unkillable_task_ids])

            # Allow the system X minutes station setup
            earliest_potential_starttime += timedelta(minutes=self.STATION_SETUP_TIME_MINUTES)

            self._propose_potential_starttime(earliest_potential_starttime)

        return kill_task_list

class DwellScheduler(PriorityScheduler):
    """ A Scheduler that searches for an allocation with a flexible start time.

        Example:

        sched = DwellScheduler(task_id, min_starttime, max_starttime, duration)
        (success, changed_tasks) = sched.allocate_resources()
        starttime = sched.starttime
    """

    def __init__(
            self,
            task_id,
            specification_tree,
            resource_estimator,
            min_starttime,
            max_starttime,
            duration,
            resource_availability_checker,
            radb: RADatabase = None,
            broker=DEFAULT_BROKER):
        """
        Create a DwellScheduler instance

        :param task_id: the ID of the task at hand
        :param specification_tree: the full specification; will be modified where needed with respect to resources
        :param resource_estimator: the ResourceEstimator function that turns a specification into resource estimates
        :param min_starttime: the task's desired minimum start time
        :param max_starttime: the task's desired maximum start time
        :param duration: the task's duration
        :param resource_availability_checker: the ResourceAvailabilityChecker to use
        :param radb: a RADatabase instance. 
        :param mom_busname: the MoM Query service bus name (default: 'lofar.ra.command')
        :param mom_servicename: the MoM Query service name (default: 'momqueryservice')
        :param broker: the message broker to use for send messages/RPC calls/etc.
        """
        super(DwellScheduler, self).__init__(
            task_id=task_id,
            specification_tree=specification_tree,
            resource_estimator=resource_estimator,
            resource_availability_checker=resource_availability_checker,
            radb=radb,
            broker=broker)

        self.min_starttime = min_starttime
        self.max_starttime = max_starttime
        self.duration = duration

        # Duration must be non-negative or weird stuff will happen
        if self.duration < timedelta(0, 0, 0):
            raise ValueError('DwellScheduler, radb_id=%s duration=%s should be >= 0' % (self.task_id, duration))

        # Time span for starttime must be sane
        if self.min_starttime > self.max_starttime:
            raise ValueError('DwellScheduler, radb_id=%s min_starttime=%s should be <= max_starttime=%s' % (self.task_id, min_starttime, max_starttime))

    def _new_starttime(self, starttime):
        """
        Set new start and end time based on the start time

        :param starttime: the new start time
        """
        self.starttime = starttime
        self.endtime = starttime + self.duration

    def _post_process_allocation(self):
        """
        After resource scheduling, update the start and end times of the task at hand in the RADB.
        """
        changed_tasks = super(DwellScheduler, self)._post_process_allocation()

        # Update the task start/endtime ONLY because the claims already were inserted with the right
        # start/endtime.
        self.radb.updateSpecification(self.task['specification_id'],
                                      starttime=self.starttime,
                                      endtime=self.endtime,
                                      commit=False)
        return changed_tasks

    def allocate_resources(self):
        """
        Scan between (min_starttime, max_starttime) to find the first possible slot where the task's required resources
        can be scheduled.

        :return: True if all the task's resources have successfully been allocated (either through dwelling the start
        time or and/or by killing tasks that have a lower priority) or False if not.
        :return: changed_tasks: tasks that had their status changed as a result of the task scheduling
        """

        changed_tasks = []
        self._new_starttime(self.min_starttime)

        while True:
            logger.info("DwellScheduler: Trying to schedule radb_id=%s with starttime=%s and endtime=%s", self.task_id, self.starttime, self.endtime)

            # Find a solution
            (scheduler_result, changed_tasks) = super(DwellScheduler, self).allocate_resources()
            if scheduler_result:
                return (True, changed_tasks)

            # Try the next slot
            new_starttime = self.earliest_potential_starttime
            if new_starttime <= self.starttime:
                raise ScheduleException("DwellScheduler radb_id=%s Cannot advance because new_starttime=%s <= self.starttime=%s", self.task_id, new_starttime, self.starttime)

            if new_starttime > self.max_starttime:
                logger.info("DwellScheduler: radb_id=%s Dwelled until the end. Earliest start time is %s but cannot go beyond %s.", self.task_id, new_starttime, self.max_starttime)
                return (False, changed_tasks)

            self._new_starttime(new_starttime)
