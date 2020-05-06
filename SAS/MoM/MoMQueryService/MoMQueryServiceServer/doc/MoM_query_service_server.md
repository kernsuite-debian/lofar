# MoM query service server {#mom_query_service_server}

Simple service listening on momqueryservice.GetObjectDetails
that sends the project details through for each requested MoM object id.


## GENERAL

### Description
 
This is the server who serves the queries over qpid in a RPC way.
A typical usage would be:
just run this service somewhere where it can access the momdb and
a qpid broker.
Make sure the bus exists: qpid-config add exchange topic <busname>



with RPC(busname, 'GetObjectDetails') as getObjectDetails:
    res, status = getObjectDetails(ids_string)
    
### Author/Owner
- *Ruud Beukema <beukema@astron.nl>*
- *Jorrit Schaap <schaap@astron.nl>*
- *Arno Schoenmakers <schoenmakers@astron.nl>*
- *Auke Klazema <klazema@astron.nl>*
- *Jan David Mol <mol@astron.nl>*

### Overview
This software is part of [MoMQueryService](@ref mom_query_service) refer to it for additional information.
- *Add a diagram* TODO
- *Add a link to the overview diagram* TODO
- *Add a link in the overview diagram to link back to this documentation*.

- - -

## DEVELOPMENT

### Analyses
*Add non-technical information and functional considerations here, like user requirements and links to minutes of 
meetings with stakeholders.* TODO

### Design
*Add technical considerations and design choices here* TODO

### Source Code
- [source code](https://svn.astron.nl/LOFAR/trunk/SAS/MoM/MoMQueryService/MoMQueryServiceClient/)
- [source code documentation](https://svn.astron.nl/lofardoc/SW-90/d5/d55/a04469.html)



### Testing
TODO tests are missing 
- *How do you run unit tests?* TODO
- *How do you run integration tests?* TODO
- *Add a link to Jenkins jobs (if available)* TODO

### Build & Deploy
This software is part of [MoMQueryService](@ref mom_query_service_build_and_deploy) refer to it for additional
information about building and deploy.

- - -
## OPERATIONS
This software is part of [MoMQueryService](@ref mom_query_service_operations) refer to it for additional
information about operations
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
- This package depends on [MoMQueryServiceCommon](@ref MoM_query_service_common) and [PyMessaging](@ref PyMessaging) and [MoMQueryServiceClient](@ref MoMQueryServiceClient)
- *Files?* TODO
- *Network locations?* TODO
- *Other?* TODO

### Security
- *Special privileges needed?* TODO
- *User login?* TODO
- *Certificates needed?* TODO
- *Other considerations?* TODO

- - -

## ADDITIONAL INFORMATION

### User Documentation

*e.g. Please refer to URL X for the User Documentation*

### Operations Documentation

*e.g. Please refer to URL X for Operations Documentation*

