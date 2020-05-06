# MoM query service {#mom_query_service}

The MoM query service consists in components a client and a server that give the possibility to
query the MoM database in a RPC fashion through the network.


## GENERAL

### Description
It makes use of [LOFAR RPC](@ref messaging_RPC) to extract information from the MoM database.
This allow to speed up the coding of frequently used database queries

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


### Testing
TODO tests are missing 
- *How do you run unit tests?* TODO
- *How do you run integration tests?* TODO
- *Add a link to Jenkins jobs (if available)* TODO

### Build & Deploy
TODO

This software is part of [MoMQueryService](@ref mom_query_service_build_and_deploy) refer to it for additional
information about building and deploy.

- - -
## OPERATIONS
TODO

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
- This package depends on [MoMQueryServiceCommon](@ref MoM_query_service_common) and [PyMessaging](@ref PyMessaging)
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