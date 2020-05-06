# Resource Assignment Estimator Package {#resource_assignment_estimator}

## GENERAL

### Description
The Resource Assignment Estimator is an RPC service which estimates which resources (and how much of each resource's capacity) are required for a given task (observation/pipeline).
It is intended to convert specifications into a resource-estimates-dict, and is currently used by the resource_assigner. It is foreseen that it can be used in the future to be used in proposal tools as well.

### Author/Owner
- *Adriaan Renting <renting@astron.nl>*


### Overview
- See description above.
- See the documenation of the [Resource Assignment system](@ref resource_assignment), of which this microservice is sub package.

- - -

## DEVELOPMENT

### Analyses
This services originated when we started the [Resource Assignment](@ref resource_assignment) project. It was recognized that we needed a tool which could convert a task specification to a list of needed resources, which could them be claimed by the resource_assigner. Be isolating such a conversion task in a standalone microservice we could/can use in other tools as well, like proposal tools.

### Design
We followed the same design choices as for the other [Resource Assignment](@ref resource_assignment) services: small, communicate via the messagebus, event driven.

### Source Code
- [source code](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment/ResourceAssignmentEstimator/)
- \ref ResourceAssignmentEstimator Source code documentation

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
    cd SAS/ResourceAssignment/ResourceAssignmentEstimator/test/
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
  cmake -DBUILD_PACKAGES="ResourceAssignmentEstimator" -DUSE_LOG4CPLUS=OFF ../..
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
- You can find all RA log file(s) in the default log dir: $LOFARROOT/var/log
- for this service: $LOFARROOT/var/log/raestimatorservice.log

### Runtime
- raestimatorservice runs under [supervisor](@ref supervisor) under user lofarsys on scu001.control.lofar, just as all other RA services.
- Start/stop it via [supervisor](@ref supervisor).
- The raestimatorservice comes with some commandline options, type raestimatorservice --help to see them. All defaults are ok for production usages.
- Restarting the service is generally ok. It has no state on it's own. There is a minor chance that while restarting it, you miss a request for an estimation, but then the caller may just call the service again.

### Interfaces (API)
- This service only listens and sends it's results on the messagebus (lofar.ra.command)
- See also doxygen generated code documentation: \ref ResourceAssignmentEstimator

### Files/Databases
- Installed in `$LOFARROOT/lib64/python2.7/site-packages/lofar/sas/resourceassignment/resourceassignmentestimator`.
- no databases are used.
- no config and/or state files are used.

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

