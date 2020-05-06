# LTA INGEST {#lta_ingest}

## General

### Description

The LTA ingest services provide the functionality for transferring the ready measurement outputs (data products) to one 
of the available Long Term Archives.

### Authors/Owners

- Jorrit Schaap <mailto:schaap@astron.nl>

### Overview

There are 4 ingest services which run individually, but work together via qpid queues and exchanges to transfer the 
export jobs.
- ingestmomadapter: 
  - this service listens on a SOAP interface for new export jobs coming from MoM, and puts the jobs on the ingest job 
    queue where they are picked up by the ingestjobmanagementserver.
  - it updates MoM dataproduct export statuses for each received started/failed/finished notification from the 
    ingesttransferserver.
- ingestjobmanagementserver:
  - handles the job queue (based on priority, retry_count, age, source host load etc)
  - dispatches new jobs to the ingesttransferserver.
  - handles started/failed/finished notification from the ingesttransferserver (by updating the job state and adjusting 
    the job queue)
  - sends email once a export job is done
- ingesttransferserver: runs an ingestpipeline in a seperate thread per job. Sends notifications on job 
  start/progress/failed/finished.
- ingestwebserver: hosts the [ingest queue website](http://10.178.1.3:9632/index.html). Gets it's info from the 
  ingestjobmanagementserver.


@startuml

title Ingest job sequence diagram

boundary MoM 
control IngestMomAdapter as ima
participant lofar.lta.ingest.jobs as jq
control IngestJobManagementServer as ijms
participant lofar.lta.ingest.jobs_for_transfer as jqft
participant lofar.lta.ingest.notification.jobmanager as ntfy_ijms
participant lofar.lta.ingest.notification.momingestadapter as ntfy_ima
participant lofar.lta.ingest.notification as ntfy
control IngestTransferServer as its

note over jq
qpid queue
end note

note over jqft
qpid queue
end note

note over ntfy_ijms
qpid queue bound to lofar.lta.ingest.notification
end note

note over ntfy_ima
qpid queue bound to lofar.lta.ingest.notification
end note

note over ntfy
qpid exchange
end note

MoM -> ima : new_job
note left : via SOAP interface on http://lexar003.control.lofar:2010
activate ima
ima -> ima : validate job
ima -> jq : submit valid job
deactivate ima

loop
	ijms -> jq : fetch job
	activate jq
	jq --> ijms
	deactivate jq

  alt fetched job
    ijms -> ijms : store new job in to_do list
  end

  ijms -> jqft : peek queue empty?
	activate jqft
	jqft --> ijms
	deactivate jqft

  alt queue empty
    ijms -> ijms : determine next job\n(based on priority, age, retry_count, etc)

    alt next job available
      ijms -> jqft : produce next job
    end
  end

	ijms -> ntfy_ijms : fetch job status notification
	activate ntfy_ijms
	ntfy_ijms --> ijms
	deactivate ntfy_ijms

  alt fetched job status notification
    ijms -> ijms : update job status\n(persist also to disk)
    alt all jobs in job_group done?
      ijms -> ijms : send email
    end
  end
end

loop
	its -> jqft : fetch job
	activate jqft
	jqft --> its
	deactivate jqft

  alt fetched job
    its -> its : run ingestpipeline\nper job in thread 
    activate its

    its -> ntfy : send job status notification
    note left : status messages:\nJobStarted/JobProgress/JobFinished/JobTransferFailed
    ntfy -> ntfy_ijms : job status notification
    ntfy -> ntfy_ima : job status notification

    deactivate its
  end
end

loop
	ima -> ntfy_ima : fetch job status notification
	activate ntfy_ima
	ntfy_ima --> ima
	deactivate ntfy_ima

  alt fetched job status notification
    ima -> MoM : update status
    note left : via https://lcs029.control.lofar:8443/
  end
end
@enduml

- - - 

## DEVELOPMENT

### Analyses
*Add non-technical information and functional considerations here, like user requirements and links to minutes of 
meetings with stakeholders.*

### Design
*Add technical considerations and design choices here*

### Source Code
- [LTA Ingest in SVN](https://svn.astron.nl/LOFAR/trunk/LTA/LTAIngest/)
- [LTA Ingest Source Code Documentation](@ref LTA)

### Testing

#### Unit Testing

Unit tests for *ingestjobmanagementserver* are available in:
    /LTA/LTAIngest/LTAIngestServer/LTAIngestAdminServer

Unit tests for *ingesttransferserver* are available in:
    /LTA/LTAIngest/LTAIngestServer/LTAIngestTransferServer

These unit tests can be run indivually with:
    ctest -R LTAIngestServer

Note that one has to (all steps except the *make install* step) the package *LTAIngest* prior to running the unit 
tests (see below).

#### Integration Testing

- *How do you run unit tests?*
- *How do you run integration tests?*
- *Add a link to Jenkins jobs (if available)*

#### Build & Deploy

##### Build locally

    svn co https://svn.astron.nl/LOFAR/<some_branch_or_trunk> <my_source_dir>
    cd <my_source_dir>
    mkdir -p build/gnu_debug
    cd build/gnu_debug
    cmake -DBUILD_PACKAGES=LTAIngest -DCMAKE_INSTALL_PREFIX=/opt/lofar/ ../..
    cd ../..
    make
    make install

##### Build using Jenkins

1 Open [the generic CentOS7 LOFAR SubSystems Jenkins project](https://support.astron.nl/jenkins/view/LOFAR%20Subsystems/view/Subsystems%20builds/job/Subsystems_CentOS7/build?delay=0sec)
2 Select buildhost (defaults to correct buildhostcentos7)
3 Select the branch you want to build:
  - For a release/rollout: Select a the latest tag
  - For a (test) build of a branch: select any branch you like (for example the one you are working on)
4 Set the MINOR_RELEASE_NR (should be equal to tag minor version number for release/rollout build)
5 Select SubSystem: LTAIngest
6 Click "Build" button, wait, build should finish successfully.

##### Deploy

Please also read the Ingest part of the common [LOFAR Release Procedure](https://www.astron.nl/lofarwiki/doku.php?id=engineering:software:releaseprocedure#update_ingest)

The procedure described below can be used for both the production environment (lexar003) and 
test environment (lexar004):

    ssh lofarsys@lexar003
    supervisorctl -p 123 stop all
    MAC_install -b LOFAR-Release-<version_number>
    supervisorctl -p 123 start all

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



