# LTA Storage Overview {#lta_storage_overview}

## General

### Description/Summary

For the Lofar LTA we have the [LTA catalogue](https://lta.lofar.eu/) which gives an overview of all described dataproducts in the LTA. There are however (quite a lot of) files in the LTA which are not described in the [LTA catalogue](https://lta.lofar.eu/).
Apart from that, we would like to have an overview of all files/directories on tape/disk in the LTA, and relate that to the current quota which we get each year from SARA, Juelich and Poznan.

So, the LTA Storage Overview services provides the following features:
 - gather information from the LTA at *file level* for each and every file in the LTA, even those which are not in the catalogue. (via ltastorageoverviewscraper)
 - provide RO/SOS with 'du-like' information on the available and used storage per site. (via ltastorageoverviewwebservice)


It uses [srm](https://sdm.lbl.gov/srm-wg/documents.html) + our grid certificates from the lexars to gather this info. The file/directory tree is stored in a database ('ltaso' at ldb003.control.lofar, and exposed via a simple overview website http://scu001.control.lofar:9632

### Authors/Owners

- Jorrit Schaap <mailto:schaap@astron.nl>

### Overview

There are 2 services which run individually on the scu001 under supervisord.
Furthermore the 2 services both use one postgres database ('ltaso' at ldb003.control.lofar) to store and retrieve the information.
- service ltastorageoverviewscraper:
  - This service runs in the background and "scrapes" information from the LTA sites using srmls (via ssh calls to lexar003/lexar004, because only the lexars have grid access and certificates).
  - The gathered information about files and directories is stored in the ltaso database.
  - It keeps track of when each directory is visited, and plans a revisit once in a while.
  - It listens for events from [Ingest](@ref lta_ingest) to schedule a scraper visit for each new directory that an ingest job creates.
- service ltastorageoverviewwebservice:
  - Very simple (and slow...) python flask webservice which generates one webpage with an overview of:
    - amount of data stored at each site (trend, delta/month, pie chart)
    - amount of quota used
    - amount of free space left

- - -

## DEVELOPMENT

### Analyses
This project originated from the need by SOS to have an overview of:
- what is in the LTA at *file level* (because not every file is in the [LTA catalogue](https://lta.lofar.eu/))
- set quota per year per LTA site.
- summarize tape usage (in (peta)bytes) per site.
- have insight in free tape space per site until the end of the quota period.
- A future requirement might be to have an (REST?) API to query for certain projects/sites/quotas/timespans etc.

Before this package ltastorageoverview existed, we generated similar overviews using srm to do a tree walk on the LTA sites, but nowadays with a large LTA this takes more than a week to complete. So we needed a background process which does the tree walk, and stores the information in a database. The scraper service was based on this original script/idea.

### Design
- The software needs to run in the background (standard lofar solution: service under supervisord)
- The infermation needs to be instantaneously retreivable (so, use a database. standard lofar database: postgres)
- Website can be simple (and slow) for now, so in this first phase we chose python flask.

### Source Code
- [LTA Storage Overview in SVN](https://svn.astron.nl/LOFAR/trunk/LTA/ltastorageoverview/)
- [LTA Storage Overview Code Documentation](@ref lta_storage_overview)

### Testing

#### Unit Testing

Unit tests are available in:
    <source-root>/LTA/ltastorageoverview/test

The tests cover:
- the creation of the ltaso database
- inserts of sites, files and directories
- checks on site and directory statistics
- a minor webservice test

#### Integration Testing

There are no integration tests since these services operate independently from other lofar software.
The 2 services work on the same (shared) database, so there is some integration there, which is tested in the unittests.

#### Build & Deploy

##### Build locally

    svn co https://svn.astron.nl/LOFAR/<some_branch_or_trunk> <my_source_dir>
    cd <my_source_dir>
    mkdir -p build/gnu_debug
    cd build/gnu_debug
    cmake -DBUILD_PACKAGES=ltastorageoverview -DCMAKE_INSTALL_PREFIX=/opt/lofar/ ../..
    cd ../..
    make
    make install

##### Build using Jenkins

1. Open [the generic CentOS7 LOFAR SubSystems Jenkins project](https://support.astron.nl/jenkins/view/LOFAR%20Subsystems/view/Subsystems%20builds/job/Subsystems_CentOS7/build?delay=0sec)
2. Select buildhost (defaults to correct buildhostcentos7)
3. Select the branch you want to build:
  - For a release/rollout: Select the latest release tag
  - For a (test) build of a branch: select any branch you like (for example the one you are working on)
4. Set the MINOR_RELEASE_NR (should be equal to tag minor version number for release/rollout build)
5. Select SubSystem: RAServices (which should be named SCU because it's more services now than just resource assigner services)
6. Click "Build" button, wait, build should finish successfully.

##### Deploy / SubSystems

The lofar package 'ltastorageoverview' is part of the RAServices subsystems package. So building and deploying the standard RAServices package for deployement on scu001 automatically gives you the ltastorageoverview services on scu001 as well.

- - -

## OPERATIONS

### Configuration
- There are no configuration files, except from the standard supervisord ini files.
- Both services come with a -h or --help option which explain the available options.

### Log Files
- Log files are located in the standard location. In this specific case, you can find ltastorageoverviewscraper.log and ltastorageoverviewwebservice.log in scu001.control.lofar:/opt/lofar/var/log/

### Runtime
- the services run under supervisord on host scu001.control.lofar
- There is no need to run these services manually from the commandline. (There is no harm in doing so either, even when the services already run under supervisord).
- It is perfectly safe to stop/start/restart the services at any time. Really, no harm is done. All information is always stored in the database.

### Interfaces (API)
- These services run standalone and have no external API.
- These services are not connected to the qpid messagebus.
- There is a start for a simple REST API in the webservice, but that's only for testing/development purposes. Might be improved when needed by SOS.
- The only user interface is the website: http://scu001.control.lofar:9632

### Files/Databases
- A single postgres 9.3+ database called 'ltaso' is used, which runs on ldb003.control.lofar
- A database create sql script is deployed (along with the python packages) in /opt/lofar/share/ltaso
- the ltaso database login credentials are stored in the standard lofar credentials location: ~/.lofar/dbcredentials/ltaso.ini
- No other files and/or databases are needed.

### Dependencies
- dependencies on 3rd party Python packages
  - python-flask
  - psycopg2
- dependencies on LTA software
  - the scraper uses srmls to get file/directory information from the LTA sites. It just uses the srm tools and the grid certificates from [Ingest](@ref lta_ingest) via ssh calls to lexar003/lexar004.
- dependencies on network:
  - a working ssh connection with key-based logging for lofarsys from scu001 to ingest@lexar003 or ingest@lexar004
- dependencies on QPID:
  - the scraper listens for events from [Ingest](@ref lta_ingest) via qpid.
    - the exchange 'lofar.lta.ingest.notification' is federated from lexar003 to scu001 (so all services on scu001 can listen for ingest events)
    - the exchange 'lofar.lta.ingest.notification' on scu001 is routed to queue 'lofar.lta.ingest.notification.for.ltastorageoverview' on which the scraper listens. We use a dedicated queue for the scraper so that no events are lost, and all ingested data is found as quickly as possible by a scraper visit.

### Security
- It is assumed that the grid certificates for user 'ingest' on lexar003/lexar004 are in place and valid. If not, contact holties@astron.nl or schaap@astron.nl
- the ltaso database login credentials are stored in the standard lofar credentials location: ~/.lofar/dbcredentials/ltaso.ini


