# RA to OTDB task specification propagator {#ra_to_otdb_task_specification_propagator}

## GENERAL

### Description
RAtoOTDBTaskSpecificationPropagator is a microservice which acts upon receiving a TaskScheduled NotificationMessage from the lofar.ra.notification messagebus. Whenever the resource assigner sends such a notification (TaskScheduled), this service reads the scheduled task specification and scheduled resources from the RADB, and converts it to a parset specification which is then submitted via the OTDBRPC to OTDB. From that moment on, the task's specifications are in OTDB and the task in OTDB has status scheduled, so it's ready to be executed.


### Author/Owner
Adriaan Renting <renting@astron.nl>

### Overview
- See description above.
- See the documenation of the [Resource Assignment system](@ref resource_assignment), of which this microservice is sub package.

- - -

## DEVELOPMENT

### Analyses
This services originated when we started the [Resource Assignment](@ref resource_assignment) project. The goal of the RA services is to schedule tasks which need resources with a limited capacity. When such claims on the needed resources can be made, we consider the task in the RADB to be scheduled and a TaskScheduled NotificationMessage is send on the lofar.ra.notification bus. In order to execute the task (and do the observation or run the pipeline) it needs to be specified in OTDB as well. For that we need a translator service which translates the RADB specs and resource claims to an OTDB parset specification. That's exactly what this service does.

### Design
We followed the same design choices as for the other [Resource Assignment](@ref resource_assignment) services: small, communicate via the messagebus, event driven.

### Source Code
- [source code in svn trunk](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment/RAtoOTDBTaskSpecificationPropagator)
- \ref RAtoOTDBTaskSpecificationPropagator Source code documentation

### Testing
- How do you run unit tests? Just as you run all the other unittests.
  -  This runs all the tests.
     ```bash
     cd build/gnu_debug
     make test
     ```
  - This runs just this package's tests
    ```bash
    cd build/gnu_debug
    cd SAS/ResourceAssignment/RAtoOTDBTaskSpecificationPropagator/test/
    make test
    ```
- How do you run integration tests? There are no integration tests.

### Build & Deploy
- This package builds as part of the RA_Services subsystem, see [RA Build & Deploy instructions](@ref resource_assignment_build_and_deploy)
- We use standard Lofar CMake to build this package. Command line build instructions from scratch:
  ```bash
  svn co https://svn.astron.nl/LOFAR/trunk/
  cd trunk
  mkdir -p build/gnu_debug
  cd build/gnu_debug
  cmake -DBUILD_PACKAGES="RAtoOTDBTaskSpecificationPropagator" -DUSE_LOG4CPLUS=OFF ../..
  make
  make install
  ```

- - -

## OPERATIONS
This service is part of the Resource Assignment subsystem. See [RA Operations documentation ](@ref resource_assignment_operations). The following subsections only mention the special files/remarks for this package.

### Configuration
- N.A. there are no configuration files for this service
- except for the supervisor ini file in $LOFARROOT/etc/supervisord.d/rotspservice.ini

### Log Files
- You can find the log file(s) in the default log dir: $LOFARROOT/var/log
- for this service: $LOFARROOT/var/log/rotspservice.log

### Runtime
- rotspservice runs under supervisord under user lofarsys on scu001.control.lofar, just as all other RA services.
- Start/stop it via supervisord. TODO: write general section on supervisord usage.
- The rotspservice comes with some commandline options, type rotspservice --help to see them. All defaults are ok for production usages.
- At this moment restarting the service might result in missed messages because we are listening on an exchange. If we miss TaskScheduled messages from the resource assigner, then they are not propagated to OTDB. TODO: rewrite this when we introduced the queue's for each service.

### Interfaces (API)
- This service only listens on the messagebus (lofar.ra.notifications), using a subclass of the generic RABusListener. It propagates each TaskScheduled notification by calling translating the RA spec & claimed resources into an OTDB parset spec, and submitting that to OTDB via the OTDBRPC.
- See also doxygen generated code documentation: \ref OTDBtoRATaskStatusPropagator

### Files/Databases
- no direct database connections are used. All communications run via the messagebus via OTDBRPC, RAPRC and RABuslistener.
- No further files are used.

### Dependencies
- The dependencies on other lofar packages are handled automatically by (LOFAR)CMake.
- The service is, like most RA services, depended on a working and [properly configured qpid broker](@ref qpid_infrastructure).
- No other dependencies on other software, tools, networks, etc exist.

### Security
Not applicable.

- - -

## ADDITIONAL INFORMATION

### User Documentation
- This service is intended for running operations for the Astron Radio Observetory. Outside users are not likely to find any use for this service.

### Operations Documentation

Use normal operational tools within the Astron Radio Observatory: tail/grep log files, use supervisord.
TODO: refer to general RO section on running/debugging/operating services.

