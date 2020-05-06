# OTDB Services {#otdb_services}

## GENERAL

The services in this package expose the detailed specifications of observations that are stored in the 
[Observation Tree Database (OTDB)](@otdb). This allows other parts of the system to use them, which is 
e.g. required for scheduling.

The package consists of the following components:
* The *TreeService* service, which serves RPC requests
* The *otdbrpc* client to interact with the TreeService
* Utilities that use otdbrpc (*getOTDBParset/setOTDBTreeStatus*)
* The *TreeStatusEvents* database watcher, which sends notification on database changes
* the *OTDBBusListener*, which can be used to listen on the notification bus in order to react to OTDB changes


### Author/Owner

- Adriaan Renting <renting@astron.nl>
- Jorrit Schaap <schaap@astron.nl>
- Jan David Mol <mol@astron.nl>


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
- [Source](https://svn.astron.nl/LOFAR/trunk/SAS/OTDB_Services/)
- *Add a link to (generated?) source code documentation.*

### Testing
Unit testing:
* ctest -V -R t_TreeService
* ctest -V -R t_TreeStatusEvents
- *How do you run integration tests?*
- *Add a link to Jenkins jobs (if available)*

### Build & Deploy
- cmake -DBUILD_PACKAGES=OTDB_Services ../..
- *Add a link to Jenkins jobs (if available)*

- - -

## OPERATIONS

### Configuration
- /SAS/OTDB_Services/config.py
- /etc/supervisord.d/OTDB_Services.ini
- /etc/supervisord.d/TreeService.ini
- /etc/supervisord.d/TreeStatusEvents.ini

### Log Files
- *Where are the log files?*

### Runtime
- *Where does it run? (which user@machine)*
- *How do I run it? (user documentation? examples? commandline parameters?)*
- *Other considerations? (what happens elsewhere when I start or stop it?)*

### Interfaces (API)
- The otdbrpc (the RPC client) writes to `lofar.otdb.command`
- The TreeService (the RPC server) reads from to `lofar.otdb.command`
- The TreeStatusEvents database watcher writes to `lofar.otdb.notification`
- The OTDBBusListener service reads from `lofar.otdb.notification`
- The getOTDBParset/setOTDBTreeStatus make use of the otdbrpc 


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
