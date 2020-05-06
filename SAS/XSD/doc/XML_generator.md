# XML generator {#XML_generator}

*This page provides the template for documenting software modules, where modules can be for example a library, service, 
or an application.*

*In order to use this template, copy its source (it is written in Markdown language) and edit it accordingy. Feel free to 
remove any explanatory text written in Italic like this text, but in case some subject is not applicable to your module: 
consider not removing its header, but add a rationale about why it is not applicable instead.*

## GENERAL

### Description
- *What does it do?*
- *Why is it needed?*

### Author/Owner

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
- *Add a link to svn (trunk).*
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
