# Resource Assignment Service {#resource_assignment_service}

This service is meant to listen for getObjectDetails from the [MoMQueryService](@ref MoM_query_service) and 
replies with the object details of the given MoM object ID.

## GENERAL

### Description
Simple Service listening on momqueryservice.GetObjectDetails
which gives the project details for each requested mom object id

It is composed by a server (radbservice), which runs on a machine that has access to the MoM database and a QPID broker,
and a client (radbclient) program that requires only access to the QPID broker. 

Obviously it is also possible to directly interact with the service through the usage of 
[MoMQueryService](@ref MoM_query_service) or doing a RPC call to the <busname>.GetObjectDetails with a
comma seperated string of mom2object id's as argument.
For instance:
```
with RPC(busname, 'GetObjectDetails') as getObjectDetails:
    res, status = getObjectDetails(ids_string)
```

The response from the service is a dict of mom2id to project-details-dict.


### Author/Owner
- *Jorrit Schaap <schaap@astron.nl>*
- *Arno Schoenmakers <schoenmakers@astron.nl>*
- *Auke Klazema <klazema@astron.nl>*
- *Jan David Mol <mol@astron.nl>*

### Overview
- *Add a diagram*
- *Add a link to the overview diagram*
- *Add a link in the overview diagram to link back to this documentation*.

- - -

## DEVELOPMENT

### Analyses
*Add non-technical information and functional considerations here, like user requirements and links to minutes of 
meetings with stakeholders.*

### Design
*Add technical considerations and design choices here*

### Source Code
[ResourceAssignmentService](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment/ResourceAssignmentService/)
[ResourceAssignmentService code documentation](https://svn.astron.nl/lofardoc/SW-90/dir_7a79603101732cc19e86e9179da6d45f.html)


### Testing
- *How do you run unit tests?*
- *How do you run integration tests?*
- *Add a link to Jenkins jobs (if available)*

### Build & Deploy
- *Add a link to general instructions or describe specifics here.*
- *Add a link to Jenkins jobs (if available)*

- - -

## OPERATIONS 

### Configuration
- *Where is the configuration file?*
- *What are the configuration options?*

### Log Files
- *Where are the log files?*

### Runtime
- *Where does it run? (which user@machine)*
- *How do I run it? (user documentation? examples? commandline parameters?)*
- *Other considerations? (what happens elsewhere when I start or stop it?)*

### Interfaces (API)
- *Describe interfaces to other applications (REST API? http requests? Messagebus?)* 
- *Other communication (user? import/export?)*

### Files/Databases
- *Which databases are used?*
- *Which files are used?*

### Dependencies
- *To/from other applications?*
- *Files?*
- *Network locations?*
- *Other?*

### Security
- *Special privileges needed?*
- *User login?*
- *Certificates needed?*
- *Other considerations?*

- - -

## ADDITIONAL INFORMATION

### User Documentation

*e.g. Please refer to URL X for the User Documentation*

### Operations Documentation

*e.g. Please refer to URL X for Operations Documentation*

