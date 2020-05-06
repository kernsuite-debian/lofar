# LOFAR Logging {#lofar_logging}

## GENERAL

### Description
This is a page that describes the common %LOFAR logging. We use a common standard for our programs in C++, Python and Java.
We also have programs in other languages and use a lot of external packages and tools, these are not covered here.

- C++ uses Log4Cplus
- Python uses the standard logging module
- Java uses ...

The standard location for logging is in /opt/lofar/var/log for both C++ and Python.
for Java the standard location is /opt/tomcat/logs?

### Author/Owner
- Marcel Loose <loose@astron.nl>
- Ruud Overeem <overeem@astron.nl>
- Hanno Holties <holties@astron.nl>
- Jan David Mol <mol@astron.nl>
- Adriaan Renting <renting@astron.nl>

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
- [LCS/Common](https://svn.astron.nl/LOFAR/trunk/LCS/Common)
- *Add a link to (generated?) source code documentation.*

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

