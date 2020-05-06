# Trigger Email Service {#trigger_email_service}

## GENERAL

### Description
The  trigger e-mail service sends out e-mails when Responsive Telescope triggers change status.  The e-mails are sent to the operators, SOS and the PIs.

### Author/Owner
Auke Klazema <klazema@astron.nl>
Jörn Künsemöller <jkuensem@physik.uni-bielefeld.de>

### Overview
- See description above.
- See the documenation of the [Responsive Telescope](@ref responsive_telescope), of which this microservice is a sub package.

- - -

## DEVELOPMENT

### Analyses
*Add non-technical information and functional considerations here, like user requirements and links to minutes of meetings with stakeholders.*

### Design
We followed the same design choices as for the [Resource Assignment](@ref resource_assignment) services: small, communicate via the messagebus, event driven.

### Source Code
- [source code in svn trunk](https://svn.astron.nl/LOFAR/trunk/SAS/TriggerEmailService)
- \ref TriggerEmailService Source code documentation

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
    cd SAS/TriggerEmailService/test/
    make test
    ```
- How do you run integration tests? There are no integration tests.

### Build & Deploy
- This package builds as part of the RT_services subsystem, see [RT Build & Deploy instructions](@ref responsive_telescope_build_and_deploy)
- We use standard LOFAR CMake to build this package.  Command line build instructions from scratch:
  ```bash
  svn co https://svn.astron.nl/LOFAR/trunk/
  cd trunk
  mkdir -p build/gnu_debug
  cd build/gnu_debug
  cmake -DBUILD_PACKAGES="TriggerEmailService" -DUSE_LOG4CPLUS=OFF ../..
  make
  make install
  ```

- - -

## OPERATIONS
This service is part of the Responsive Telescope subsystem. See [RT Operations documentation ](@ref responsive_telescope_operations). The following subsections only mention the special files/remarks for this package.

### Configuration
- N.A. there are no configuration files for this service
- except for the supervisor ini file in $LOFARROOT/etc/supervisord.d/TriggerEmailService.ini

### Log Files
- You can find the log file(s) in the default log dir: $LOFARROOT/var/log
- for this service: $LOFARROOT/var/log/TriggerEmailService.log

### Runtime
- TriggerEmailService runs under supervisord under user lofarsys on scu001.control.lofar, just as all other RA services.
- Start/stop it via supervisord. TODO: write general section on supervisord usage.
- The TriggerEmailService has no commandline options.
- At this moment restarting the service might result in missed messages because we are listening on an exchange.  If we miss TriggerAdded messages then e-mails will not be sent.  TODO: rewrite this when we introduced the queue's for each service.

### Interfaces (API)
- This service only listens on the messagebus (lofar.trigger.notifications, lofar.otdb.notification), using subclasses of the generic AbstractBusListener and OTDBBusListener.
- See also doxygen generated code documentation: \ref TriggerEmailService

### Files/Databases
- no direct database connections are used. All communications run via the messagebus with MoMQueryRPC, OTDBBusListener and AbstractBusListener.
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
