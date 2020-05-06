# Resource Assignment Database {#resource_assignment_database}

## GENERAL

### Description
This python package provides an interface via the module `radb.py` which performs SQL database queries on the Resource Assigner Database (RADB). It also provides the Python mini service `radbpglistener` which is a Postgres listener that publishes changes in the RADB SQL tables on the QPID resource assignment notification bus `lofar.ra.notification`.  A corresponding Python client for these notifications is implemented in `radbbuslistener.py`.  This package is used amonst others by the web scheduler.


### Author/Owner
- Jorrit Schaap <schaap@astron.nl>
- Auke Klazema <klazema@astron.nl>
- Ruud Beukema <beukema@astron.nl>

### Overview
- See description above.
- See the documenation of the [Resource Assignment system](@ref resource_assignment), of which this is a sub package.

- - -

## DEVELOPMENT

### Analyses
This package originated when we started the [Resource Assignment](@ref resource_assignment) project. We needed a database in which we could model the LOFAR instrument as a generic collection of resources, from which a subset can be claimed (partially or fully) for a given task such as an observation or a pipeline. On top of the database we needed a python API to insert/update/delete tasks and claims on resources, and we wanted to send NotificationMessages on the messagebus for each change in certain tables (like the task table).

### Design
We followed the same design choices as for the other [Resource Assignment](@ref resource_assignment) services: small, communicate via the messagebus, event driven.
For the database we've chosen Postgresql.

### Source Code
- [source code](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment/ResourceAssignmentDatabase/)
- see also the radb/sql subfolder with the database create scipts. These are deployed on production in $LOFARROOT/share/radb/sql.
- \ref ResourceAssignmentDatabase Source code documentation


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
    cd SAS/ResourceAssignment/ResourceAssignmentDatabase/test/
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
  cmake -DBUILD_PACKAGES="ResourceAssignmentDatabase" -DUSE_LOG4CPLUS=OFF ../..
  make
  make install
  ```

- - -

## OPERATIONS
This package is part of the Resource Assignment subsystem. See [RA Operations documentation ](@ref resource_assignment_operations). The following subsections only mention the special files/remarks for this package.

### Configuration
- Any python program using radb.py has to supply [database credentials](@ref dbcredentials) for the RADB. These can be found on the production system in ~/.lofar/dbcredentials/radb.ini
- the supervisor ini file in $LOFARROOT/etc/supervisord.d/radbpglistener.ini

### Log Files
- You can find all RA log file(s) in the default log dir: $LOFARROOT/var/log
- for this package: $LOFARROOT/var/log/radbpglistener.log

### Runtime
- radbpglistener runs under [supervisor](@ref supervisor) under user lofarsys on scu001.control.lofar, just as all other RA services.
- Start/stop it via [supervisor](@ref supervisor).
- The radbpglistener comes with some commandline options, type radbpglistener --help to see them. All defaults are ok for production usages.
- Restarting the radbpglistener service is generally ok. It has no state on it's own. There is a minor chance that while restarting it, you miss a changes in the database.

### Interfaces (API)
- This radbpglistener service only sends NotificationMessages on the lofar.ra.notification messagebus.
- See doxygen generated code documentation: \ref ResourceAssignmentDatabase

### Files/Databases
- Installed in `$LOFARROOT/lib64/python2.7/site-packages/lofar/sas/resourceassignment/database`.
- The RADB postgres database runs on ldb003, database: resourceassignment

### Dependencies
- The dependencies on other lofar packages are handled automatically by (LOFAR)CMake.
- The radbpglistener service is, like most RA services, depended on a working and [properly configured qpid broker](@ref qpid_infrastructure).
- A working RADB postgres database.
- No other dependencies on other software, tools, networks, etc exist.

### Security
Login credentials to the RADB postgres database are handled in using the LOFAR [database credentials](@ref dbcredentials) system.

- - -

## ADDITIONAL INFORMATION

### User Documentation
- This service is intended for running operations for the Astron Radio Observetory. Outside users are not likely to find any use for this service.

### Operations Documentation

Use normal operational tools within the Astron Radio Observatory: tail/grep log files, use supervisord.
TODO: refer to general RO section on running/debugging/operating services.

