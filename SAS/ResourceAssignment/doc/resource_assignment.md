# Resource Assignment Package {#resource_assignment}

# Resource Assignment subsystem

## GENERAL

### Description
The Resource Assignment (RA) system sits between the systems that handle the scientific and system specifications (MoM) 
and the task management systems (SAS/MAC/OTDB).
The task of the RA system is to translate a system specification into a specific resource assignment, 
which then together are the Virtual Intrument that is given to the task management (as an OTDB VIC Tree) 
to execute the task.

The RA system takes a task's system specification, estimates which resources are needed to execute that task
and then checks against available resources to see if it can find a solution which actual resources to use
to execute the task.

Resources include things like network, storage, processing, antennas, station hardware, and often most importantly time.

####Design goals
*  The RA system is meant as an automated replacement for several manual and offline steps in the %LOFAR system. This allows
automatic operation 24/7 with response times within seconds. This hopefully saves a lot of manpower, allows for more efficient
operation of the telescope and automated reactions to events.
*  The RA system is designed to use a more consistent Virtual Instrument model, modelling all resources
in a database, with the goal of creating a more generic system that can be easily adapted to changing hardware, without
having to update hardcoded values in a lot of source code locations.
* The user interface was also redesigned to allow a (near) real-time view on the system, and allow multiple users to
interact with the system in a manner visible to other users.


### Author/Owner
* Adriaan Renting <renting@astron.nl>
* Jorrit Schaap <schaap@astron.nl>
* various developers for the sub-systems of the RA system

### Overview
See [Wiki documentation Resource Assigner](https://www.astron.nl/lofarwiki/doku.php?id=rrr:redesign_resource_assignment_system)
Updated diagrams (in graphml/odf format) can be found in the [SVN documentation on SAS redesign for responsive telescope](https://svn.astron.nl/LOFAR/trunk//SAS/doc/SAS_redesign_for_responsive_telescope/)

TODO
- *Add a diagram*
- *Add a link to the overview diagram*
- *Add a link in the overview diagram to link back to this documentation*.

- - -

## DEVELOPMENT

### Analyses
The main reasons for the Resource Assignment system are explained in detail in the [SAS/doc/SAS_redesign_for_responsive_telescope]
documents. The core of this analysis is that we need an automated system and that meant replacing the [Scheduler](@ref scheduler_package).
It was important to not just replace the functionality, but also keep in mind the 
[Non-functional Requirements](@ref resource_assignment_non_functional_requirements).

The main functional requirements are:
- It should be able to assign resources of a single task below 10 seconds, preferably around 1 second.
- It should be able to handle 3000 tasks/week.
- It should handle 300 resources per task.
- It should handle a total of a million resource claims a week.
- The Virtual Instrument Model should closely match actual hardware.
- The Virtual Instrument Model should be adaptable with minimal to no code changes.
- The user interfaces should give a (near) real-time view of the system.

Furthermore the goal was to follow the LOFAR Meta [Architecture Principles](@ref lofar_meta_architecture_principles).

### Design
Initially the thoughts were to implement the new GUI in Qt, as this would maybe allow keeping some of the Scheduler code
and would make it more predictable to reach some of the Non-Functional Requirements. In the end the choice was made
to make a GUI using WEb 3.0 technologies as this might make it more portable.
There were serious concerns about the performance of such a solution, but a demo implementation showed that it should be
possible to reach a performant enough application.

A choice was made to introduce an ERROR/error/Error status to several parts of the system because it was identified that 
a lot of Non-functional Requirements related to the system not having this status and thus displaying either an
incorrect old or new status if a problem occurred in going from one status to another status.

The choice was made to keep all consistency checking in the database so that other services could be duplicated for 
performance reasons when needed, could be largely state-less for easy restarting and operations. This also reduced the 
number of round-trips to the database, introducing less latency and reducing performance bottlenecks in the 
applications.

It was decided to manage the large number of small services using [supervisord](TODO link).

All the interactions with legacy systems were relegated to separate services as much as possible, allowing for loose coupling 
to legacy systems, and easier replacement of connected systems.

The initial design was to use a new model for system specifications, but due to time constraints and the choice by
management to freeze MoM and not finish the required implementation changes in MoM, the current system uses a lot
of the OTDB VIC Tree implementation as an internal structure as well.

### Source Code
- The source code can be found under [SAS/OTDB Services](https://svn.astron.nl/LOFAR/trunk/SAS/OTDB_Services) and 
[SAS/ResourceAssignment](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment) and 
[SAS/MoM/MoMQueryService](https://svn.astron.nl/LOFAR/trunk/SAS/MoM/MoMQueryService).
- *Add a link to (generated?) source code documentation.*

### Testing
- *How do you run unit tests?*
- *How do you run integration tests?*
- *Add a link to Jenkins jobs (if available)*

### Build & Deploy {#resource_assignment_build_and_deploy}
- Currently the system is known as [RA Services](TODO link) within the Cmake and Jenkins systems.
- *Add a link to Jenkins jobs (if available)*

- - -

## OPERATIONS {#resource_assignment_operations}

### Configuration
The configuration happens though the standard [Database configuration](TODO link), [supervisord](TODO link) 
ini files and ...

### Log Files
Log files are in the standard [LOFAR log](TODO link) locations for each service.

### Runtime
- All the services run on scu001 (production) and scu099 (test) under supervisord.
- You install through [MAC Install](TODO link) and/or Jenkins scripts that use those.
- All services should start automatically when [supervisord](TODO link) starts.
- There is a web user interface to [supervisord](TODO link) where you can start/stop/restart each service
and inspect the logging.

### Interfaces (API)
- *Describe interfaces to other applications (REST API? http requests? Messagebus?)* 
- *Other communication (user? import/export?)*

### Files/Databases
- The Resource Assignment system uses the [ResourceAssignmentDatabase](TODO link) and talks with MoM through
the [MoMqueryService](@ref mom_query_service) and to [OTDB](@ref otdb) trough the [OTDB Services](@ref otdb_services).
- *Which files are used?*

### Dependencies
- It requires [QPID](TODO link) to be set up correctly and have all the required queues and exchanges.
- It requires [CEP4 Robinhood](TODO link) to retrieve storage space information of the cluster.
- It requires [DRAGNET ????](TODO link) to receive storage space information of the [DRAGNET](TODO link) cluster.
- It requires [Jenkins](TODO link), [MAC Install](TODO link), [supervisord](TODO link) to install and run, see Runtime.
- *Other?*

### Security
- The whole system runs as lofarsys.
- Currently we run without Kerberos, but we have used versions that use Kerberos to secure QPID communication.
- We need better passwords on [supervisord]
- *Other considerations?*

- - -

## ADDITIONAL INFORMATION

### User Documentation

*e.g. Please refer to URL X for the User Documentation*

### Operations Documentation

*e.g. Please refer to URL X for Operations Documentation*

