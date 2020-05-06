
# WinCCWrapper Overview {#winccwrapper_overview}

## General

### Description/Summary

The WinCCWrapper library is a simple C++ wrapper around the difficult to use WinCC_OA API. Of course one could always still choose use the WinCC_OA API which provides more features than this simple wrapper. This WinCCWrapper is aimed at providing a simple API to set and get datapoints into a wincc database. All calls are blocking/synchronous (where the underlying WinCC_OA API is asynchronous).

This WinCCWrapper library has the following features:
- set/get datapoints for the most common datatypes (int, long, float, bool, string, time_t)
- mark datapoints as valid/invalid.
- "connect" to changes in datapoints: whenever a 'connected' datapoint is changed (by whoever from whereever) then a supplied callback function is called.

Boost-python bindings are provided as well, exposing the same API in python.


### Authors/Owners

- Auke Klazema <mailto:klazema@astron.nl>
- Jorrit Schaap <mailto:schaap@astron.nl>

### Overview

This package builds a c++ library, and python bindings. For further details, see Description above.

- - -

## DEVELOPMENT

### Analyses
This library originated from the Responsive Telescope project which needed a means to use the station monitoring information available in the wincc database. It was later extended in the APERTIF project to provide a means to set/get the validness of datapoints.

The folling feaures were required, and implemented:
- set/get datapoints for the most common datatypes (int, long, float, bool, string, time_t)
- mark datapoints as valid/invalid.
- "connect" to changes in datapoints: whenever a 'connected' datapoint is changed (by whoever from whereever) then a supplied callback function is called.

Because the WinCC_OA API is hard to use, we decided to implement this simple wrapper.
Because the WinCC_OA API is in C++, this wrapper needed to be written in C++ as well.
Because we needed to have the same API available in python as well, we decided to create boost-python bindings.


### Design
No fancy design needed. This is just a library with a few classes wrapping the complicated WinCC_OA API into a simple API.

### Source Code
- [WinCCWrapper in SVN](https://svn.astron.nl/LOFAR/branches/SW-26_WinCC/LCS/WinCCWrapper)
- [WinCCWrapper Code Documentation](@ref winccwrapper_overview)

### Testing

#### Unit Testing

We decided not to provide unit tests, because that would require to write a quite large mocked version of the WinCC_OA API, which would be bigger and more complex than the wrapper classes themselves.

#### Integration Testing

When BUILD_TESTING is ON, then little test programs are built: WinCCSet and WinCCGet. They can be run from the cmdline (on a host where WinCC is running) and be used to test whether you can successfully set and/or get a datapoint. This is a manual test.

#### Build & Deploy

This library needs a c++11 compiler.
Dependencies on other libraries are automatically found by cmake, and otherwise reported which are missing.

##### Build locally

    svn co https://svn.astron.nl/LOFAR/<some_branch_or_trunk> <my_source_dir>
    cd <my_source_dir>
    mkdir -p build/gnu_cxx11debug
    cd build/gnu_cxx11debug
    cmake -DBUILD_PACKAGES=WinCCWrapper -DUSE_LOG4CPLUS=OFF -DCMAKE_INSTALL_PREFIX=/opt/lofar/ ../..
    cd ../..
    make
    make install

##### Build using Jenkins

There are no special Jenkins jobs for this package specifically. Such a job is also not needed. CMake will automatically take care of building this package whenever a package which is build by Jenkins is dependent on WinCCWrapper.

##### Deploy

There is no special Jenkins job to deploy this package specifically. Such a job is also not needed. The library from this package is deployed automatically thanks to cmake/jenkins whenever another package is deployed which depends on this package.

- - -

## OPERATIONS

### Configuration
- There are no configuration files.

### Log Files
- This library does not produce log files. A program using this library could produce logfiles, and these log files will contain the log lines issued by this library.

### Runtime
- This library just loads whenever a using program is started.

### Interfaces (API)
- It's a library. See the source code documentation for the api.

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



