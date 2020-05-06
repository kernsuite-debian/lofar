# Task Prescheduler {#task_prescheduler}

Scheduling a task requires filling in system requirements.

Usually this task is performed by operators unfortunately this is not always possible expecially
when the task is specified automatically by a trigger in the system.
The TaskPrescheduler carries out this task.

## GENERAL

### Description
Class to take a task on approved and add the information needed to put it on prescheduled.
This means adding/updating some Cobal keys, selecting available stations,
selecting the right timeslot and updating start/end time.

### Author/Owner
- *Auke Klazema <klazema@astron.nl>*
- *Jan David Mol <mol@astron.nl>*
- *Adriaan Renting <renting@astron.nl>*

### Overview
*TODO* 

- - -

## DEVELOPMENT

### Analyses
*TODO*

### Design
*TODO*

### Source Code
- [source code](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment/TaskPrescheduler/)
- [source code documentation](https://svn.astron.nl/lofardoc/SW-90/d7/df4/a04564.html)

### Testing
- Standard way to run tests (TODO add a common link)
- There are no integration tests. They might be needed to test the integration with
   OTDB_RPC, RADB_RPC, MOM_RPC
- *Add a link to Jenkins jobs (if available)* TODO

### Build & Deploy
This service is part of the Resource Assignment subsystem. See [RA Build & Deploy documentation](@ref resource_assignment_build_and_deploy). The following subsections only mention the special files/remarks for this package.
- *Add a link to general instructions or describe specifics here.* TODO
- *Add a link to Jenkins jobs (if available)* TODO

- - -

## OPERATIONS
This service is part of the Resource Assignment subsystem. See [RA Operations documentation](@ref resource_assignment_operations). The following subsections only mention the special files/remarks for this package.
### Configuration
TODO write command section about supervisor


### Log Files
- *Where are the log files?* TODO

### Runtime
- *Where does it run? (which user@machine)* TODO
- *How do I run it? (user documentation? examples? commandline parameters?)* TODO
- *Other considerations? (what happens elsewhere when I start or stop it?)* TODO

### Interfaces (API)
- *Describe interfaces to other applications (REST API? http requests? Messagebus?)* TODO
- *Other communication (user? import/export?)* TODO

### Files/Databases
- *Which databases are used?* TODO
- *Which files are used?* TODO

### Dependencies
[PyMessaging](@ref PyMessaging) 
[ResourceAssignmentService](@ref resource_assignement_service)
[OTDB_Services](@ref otdb_services)
[MoMQueryServiceClient](@ref mom_query_service_client)
[pyparameterset](@ref pyparameterset)
[RACommon](@ref RA_Common)
- *Files?* No
- *Network locations?* No
- *Other?* No

### Security
- *Special privileges needed?* TODO
- *User login?* TODO
- *Certificates needed?* TODO
- *Other considerations?* TODO

- - -

## ADDITIONAL INFORMATION

### User Documentation

*e.g. Please refer to URL X for the User Documentation* TODO

### Operations Documentation

*e.g. Please refer to URL X for Operations Documentation* TODO

