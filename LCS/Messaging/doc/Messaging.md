# Messaging {#messaging}

## GENERAL

### Description
This module contains code for the C++ library `libmessaging.so` and a base class for Python mini services.  The C++ library can send and receive QPID messages while the Python base class communication is done through RPCs.

### Author/Owner
- Jorrit Schaap <schaap@astron.nl>
- Jan David Mol <mol@astron.nl>

### Overview
The Python class `AbstractBusListener` is the base class for Python services that are listening on the QPID bus for a certani type of message.  The following Python services inherit from `AbstractBusListener`:

- `Service`:  This is the base class for RPC micro services.
- `TriggerNotificationListener`
- `OTDBBusListener`
- `IngestBusListener`
- `DataManagementBusListener`
- `RABusListener`
- `RATaskSpecifiedBusListener`
- `RADBBusListener`

The `libmessaging.so` library is used by the following modules:

- `WinCCPublisher`
- - -

## DEVELOPMENT

### Analyses
*TODO*

### Design
*TODO*

### Source Code
[LCS/Messaging](https://svn.astron.nl/LOFAR/trunk/LCS/Messaging)

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
This module cannot be configured.

### Log Files
This module does not create log files.

### Runtime
Not applicable.

### Interfaces (API)
*TODO*

### Files/Databases
Not applicable.

### Dependencies
- QPID
- Common
- PyCommon

### Security
Not applicable.

- - -

## ADDITIONAL INFORMATION

### User Documentation

*e.g. Please refer to URL X for the User Documentation*

### Operations Documentation

*e.g. Please refer to URL X for Operations Documentation*

