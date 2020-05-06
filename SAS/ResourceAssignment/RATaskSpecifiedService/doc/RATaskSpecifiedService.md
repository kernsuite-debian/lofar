# RA Task Specified Service {#resource_assigner_ra_task_specified_service}

# Software Module RATaskSpecifiedService

## GENERAL

### Description
- This service listens on OTDB status changes, requests the parset of such jobs including their predecessors, and posts them on a bus for the Resource assigner.
- The RATaskSpecifiedService triggers the Resource Assigner to assigne resources on a specified task and gathers the required task specs.

### Author/Owner

- Jan David Mol <mol@astron.nl>
- Jorrit Schaap <schaap@astron.nl>
- Auke Klazema <klazema@astron.nl>

### Overview
- Find diagrams (in graphml/odf format) can be found in the [SVN documentation on SAS redesign for responsive telescope](https://svn.astron.nl/LOFAR/trunk//SAS/doc/SAS_redesign_for_responsive_telescope/)
- Find outdated diagrams in png format in the wiki page [resource assigner redesign](https://www.astron.nl/lofarwiki/doku.php?id=rrr:redesign_resource_assignment_system). This service fits in the OTDB Task Watcher in the first diagram, and in the ResourceAssignService of the detailed view. It writes to the lofar.ra.notification bus.

- - -

## DEVELOPMENT

### Analyses
- *todo: Add non-technical information and functional considerations here, like user requirements and links to minutes of
meetings with stakeholders.*

### Design
- *todo: Add technical considerations and design choices here*

### Source Code
- [Source code](https://svn.astron.nl/LOFAR/trunk/SAS/ResourceAssignment/RATaskSpecifiedService/)
- [Documentation](https://svn.astron.nl/lofardoc/trunk/) *todo:* fix link

### Testing
- For unit testing run: ctest -V -R tRATaskSpecified
- *todo: How do you run integration tests?*
- *todo: Add a link to Jenkins jobs (if available)*

### Build & Deploy
- in build/gnucxx11_opt/: cmake -DBUILD_PACKAGES=RATaskSpecifiedService ../..
- *todo: Add a link to Jenkins jobs (if available)*

- - -

## OPERATIONS

- This service is part of the Resource Assignment subsystem. See [RA Operations documentation ](@ref resource_assignment_operations). The following subsections only mention the special files/remarks for this package.

### Configuration
- etc/supervisord.d/rataskspecifiedservice.ini

### Log Files
- RATaskSpecified.log

### Runtime
- Controlled by supervisord.
- Executed by user `lofarsys`.

### Interfaces (API)
- Listens on QPID channel  `lofar.otdb.notification`
- Gathers info via RPC calls to otdb (`lofar.otdb.command`), radb (`lofar.ra.command`) and mom (`lofar.ra.command`)
- Writes to QPID channel `lofar.ra.notification`

### Files/Databases
- Installed in `lofar/sas/resourceassignment/rataskspecified/`
- *Which files are used?*

### Dependencies
- PyMessaging
- PyCommon
- pyparameterset
- OTDB_Services

### Security
- Executed by `supervisord`, a restart needs supervisord credentials.

- - -

## ADDITIONAL INFORMATION

### User Documentation

*todo: Please refer to URL X for the User Documentation*

### Operations Documentation

*todo: Please refer to URL X for Operations Documentation*

