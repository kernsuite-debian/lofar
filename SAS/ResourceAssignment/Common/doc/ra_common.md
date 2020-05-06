# Resource Assignment Common Package {#resource_assignment_common}

## GENERAL

### Description

The packages holds the commons code for the Resource Assignment. For now it only
hold the Specification class.

The specification class created because multple classes used specification
values in dicts. The dict was not very readable and difficult to use. And by
extracting it out to its own class all values regarding the specifications are
in one spot. The Specification can be filled from OTDB, MoM and RADB. But also
based on the old dict structure. The Specification can be modified and then
submitted to RADB and certain changes to OTDB and MoM.

### Author/Owner

- Adriaan Renting renting@astron.nl

### Overview

No diagrams available at this moment.

- - -

## DEVELOPMENT

### Analyses

No analyses documentation available.

### Design

The current design of the Specification class comes out of a refactor action. The code comments mentions the wish to add more OO based design to it. The code now does not enforce consistency.

### Source Code
- https://svn.astron.nl/viewvc/LOFAR/trunk/SAS/ResourceAssignment/Common/
- https://svn.astron.nl/lofardoc/trunk/d6/d18/a01925.html

### Testing
`make test` will run all tests available for Specification class these are all unit tests.

The following jenkins job could be used to run tests for the Resource Assignment Common Package. 
https://support.astron.nl/jenkins/view/LOFAR%20Subsystems/view/Subsystems%20builds/job/Subsystems_CentOS7/ Its get build together with other classes by the RAServices subsystem. You do need to check the RUN_TESTS box so that the tests get run.

### Build & Deploy
The Resource Assignment Common Package is used by other packages and gets build as a dependency of another project. If only the Common package needs to be build one could run `cmake -DBUILD_PACKAGES=\'RACommon\'; make`. Deployment is done again as a dependency and as part of the RAService subsystem. Jenkins needs to be used to build and either use the MAC_install scripts or the dedicated jenkins job. https://support.astron.nl/jenkins/view/LOFAR%20Install/job/Systemwide%20LOFAR%20Deployment/

- - -

## OPERATIONS

### Configuration
The package only contains common classes that do not require configuration.

### Log Files
The logs a witten to the supplied logger for the Specification class. So it depends.

### Runtime
The package only contains common classes so no standalone runtime code.

### Interfaces (API)
The package only has the class api. See code class documentation

### Files/Databases
No direct databases or files are involved.

### Dependencies
The package has dependencies to rpc clients.

### Security
At the moment no security issues are known.

- - -

## ADDITIONAL INFORMATION

### User Documentation

No user documentation available. Only the code documentation.

### Operations Documentation

No operations documentation available. Only the code documentation.

