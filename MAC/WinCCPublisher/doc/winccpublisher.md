 
# WinCCPublisher Overview {#winccpublisher_overview}

## General

### Description/Summary

The WinCCPublisher package builds an executable which publishes MonitoringMessages on a configurable qpid bus whenever a datapoint in the wincc database changes for a configurable list of datapoints. You can use it to run 24/7 and monitor certain datapoints in the wincc database. For each change on a datapoint, a MonitoringMessage is published on the messagebus. Then just let your other applications listen on that messagebus, and do fancy stuff when you receive such a message.

This package is a proof of concept and not used in production yet.

### Authors/Owners

- Auke Klazema <mailto:klazema@astron.nl>
- Jorrit Schaap <mailto:schaap@astron.nl>

- - -

## DEVELOPMENT

### Analyses
This application originated from the Responsive Telescope project which needed a means to use the station monitoring information available in the wincc database.

The folling feaures were required, and implemented:
- "connect" to changes in datapoints: whenever a 'connected' datapoint is changed (by whoever from whereever) then a message should be published on the messagebus.

This application builds upon the features provided by the [WinCCWrapper](@ref winccwrapper_overview) and [Messaging](@ref messaging_overview) libraries.

### Design
This application builds upon and combines features from the WinCCWrapper and Messaging libraries. It uses the connect datapoints feature from the WinCCWrapper, and creates and sends a MonitoringMessage on the messagebus in the datapoint changed callback function.

### Source Code
- [WinCCPublisher in SVN](https://svn.astron.nl/LOFAR/branches/SW-26_WinCC/MAC/WinCCPublisher)
- [WinCCPublisher Code Documentation](@ref winccpublisher_overview)

### Testing

#### Unit Testing

We decided not to provide unit tests, because that would require to write a quite large mocked version of the WinCC_OA API, which would be bigger and more complex than the application itself.

#### Integration Testing

When BUILD_TESTING is ON, then a little test program is built: wincclistener. It can be used to listen on the same qpid messagebus as where the winccpublisher published it's messages on. Set any of the 'connected' datapoints, and check if the MonitoringMessage is received and printed by the wincclistener. This is a manual test.

#### Build & Deploy

- This application needs a c++11 compiler.
- Dependencies on other libraries are automatically found by cmake, and otherwise reported which are missing.


##### Build locally

    svn co https://svn.astron.nl/LOFAR/<some_branch_or_trunk> <my_source_dir>
    cd <my_source_dir>
    mkdir -p build/gnu_cxx11debug
    cd build/gnu_cxx11debug
    cmake -DBUILD_PACKAGES=WinCCPublisher -DUSE_LOG4CPLUS=OFF -DCMAKE_INSTALL_PREFIX=/opt/lofar/ ../..
    cd ../..
    make
    make install

##### Build using Jenkins

There are no special Jenkins jobs for this package specifically. Such a job is also not needed. CMake will automatically take care of building this package whenever a package which is build by Jenkins is dependent on WinCCPublisher.

##### Deploy

There is no special Jenkins job to deploy this package specifically. Such a job is also not needed. The application from this package is deployed automatically thanks to cmake/jenkins whenever another package is deployed which depends on this package.

- - -

## OPERATIONS

### Configuration
- WinCCPublisher.conf in the same dir as the winccpublisher application.

### Log Files
- This application logs to stdout.

### Runtime
- Just run 'winccpublisher' from the command line.

### Interfaces (API)
- This application sends MonitoringMesssages on the bus upon each change of a connected datapoint.

### Files/Databases
- It depends on a running WINCC_OA instance (which run on the mcu's)
- No other files and/or databases are needed.

### Dependencies
- WINCC_OA 3.15 (API, and runtime, which are installed on mcu's and the buildhostcentos7)

### Security
- No login credentials are needed.

- - -

## ADDITIONAL INFORMATION

### User Documentation

N.A.

### Operations Documentation

N.A.



