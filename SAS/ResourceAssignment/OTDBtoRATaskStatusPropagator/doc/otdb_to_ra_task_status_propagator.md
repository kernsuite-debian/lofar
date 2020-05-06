# OTDB to RA task status propagator {#otdb_to_ra_task_status_propagator}

# Software Module X

## GENERAL

### Description
The OTDB to RA task status propagator service is a micro service which updates any task status change in OTDB to the RADB. 
Due to historical reasons Lofar tracks it's tasks in three different databases: MoM, OTDB and RABD. The state of each task needs to be in sync between these databases, and this service takes care of the OTDB->RADB route. It is intended that we move to a single task database one day, and then this service becomes obsolete.

### Author/Owner
-  Jorrit Schaap schaap@astron.nl

### Overview

The OTDB to RA task status propagator service is a micro service which updates any task status change in OTDB to the RADB. 
It connects with a derived class of the OTDBBusListener to the lofar.otdb.notification messagebus. It handles each received NotificationMessage from that bus, and propagates the OTDB task status changes via the RARPC into the RADB.
- - -

## DEVELOPMENT

### Analyses
This services originated when we started the [Resource Assignment](@ref resource_assignment) project. It was quickly recogninzed that we needed to keep the different databases which track tasks in sync, and hence the need to this service was born. 

### Design
We followed the same design choices as for the other [Resource Assignment](@ref resource_assignment) services: small, communicate via the messagebus, event driven. It makes use of common components like the OTDBBusListener and RARPC.

### Source Code
- [Source code in svn trunk](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment/OTDBtoRATaskStatusPropagator)
- \ref OTDBtoRATaskStatusPropagator Source code documentation

### Testing
- There are no unit tests (yet) for this package. TODO: write unittests
- There are no automated integration tests (yet) for this package. TODO: write integration tests

### Build & Deploy
- This package builds as part of the RA_Services subsystem, see [RA Build & Deploy instructions](@ref resource_assignment_build_and_deploy)
- We use standard Lofar CMake to build this package. Command line build instructions from scratch:
  ```bash
  svn co https://svn.astron.nl/LOFAR/trunk/
  cd trunk
  mkdir -p build/gnu_debug
  cd build/gnu_debug
  cmake -DBUILD_PACKAGES="OTDBtoRATaskStatusPropagator" -DUSE_LOG4CPLUS=OFF ../..
  make
  make install
  ```
- - -

## OPERATIONS

This service is part of the Resource Assignment subsystem. See [RA Operations documentation ](@ref resource_assignment_operations). The following subsections only mention the special files/remarks for this package.


### Configuration
- N.A. there are no configuration files for this service

### Log Files
- Standard location: $LOFARROOT/var/log/otdbtorataskstatuspropagator.log

### Runtime
- otdbtorataskstatuspropagator runs under supervisord under user lofarsys on scu001.control.lofar, just as all other RA services.
- Start/stop it via supervisord. TODO: write general section on supervisord usage.
- The otdbtorataskstatuspropagator comes with some commandline options, type otdbtorataskstatuspropagator --help to see them. All defaults are ok for production usages. 
- At this moment restarting the service might result in missed messages because we we listening on an exchange. If we miss status update messages from OTDB, then they are not reflected in RADB. TODO: rewrite this when we introduced the queue's for each service. 

### Interfaces (API)
- This service only listens on the messagebus, using a subclass of the generic OTDBBusListener. It propagates each OTDB task status change by calling task status update methods on the RARPC. When a tasks finishes, then it also updates the task's endtime in the RADB to now.

### Files/Databases
- This service interfaces with OTDB (listening) and RADB (writing) via the messagebus, not via direct database connections.
- No further files are used.

### Dependencies
- This service is dependend on package [OTDB_Services](@ref otdb_services) which defines the OTDBBusListener. 
- This service is dependend on package [ResourceAssignmentService](@ref resource_assignment_service) which defines the RARPC. 
- At runtime, this service is loosely coupled to the OTDB TreeStatusEvents service which sends status update messages on which the OTDBBusListener reacts.
- At runtime, this service is loosely coupled via the messagebus to the ResourceAssignmentService, which handles the RARPC calls and interacts with the RADB.
- At runtime, this service connects (by default) to the local qpid-broker which needs to run, and be properly configured with [QPIDInfrastructure](@ref qpid_infrastructure)


### Security
- This service normally runs in production under supervisord under user lofarsys at scu001.control.lofar
- The loosely coupled services TreeStatusEvents and ResourceAssignmentService do need OTDB and RADB database credentials.

- - -

## ADDITIONAL INFORMATION

### User Documentation

- This service is intended for running operations for the Astron Radio Observetory. Outside users are not likely to find any use for this service. 

### Operations Documentation

Use normal operational tools within the Astron Radio Observatory: tail/grep log files, use supervisord.
TODO: refer to general RO section on running/debugging/operating services.

