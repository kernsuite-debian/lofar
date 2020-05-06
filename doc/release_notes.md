# Release Notes {#release_notes}

## LOFAR 2.22.6 (Sep 21th, 2017)

### Ingest

- Fixed a bug in the ingest not sending mails

## LOFAR 2.22.5 (Sep 20th, 2017)

### Imaging pipeline

- Fixed a bug in the imaging pipeline not recognizing SPARSE

## LOFAR 2.22.4 (Sep 19th, 2017)

### XML Generator

- Fixed a bug in the xmlgenerator when trying to upload on approved with -a.

## LOFAR 2.22.3 (Sep 18th, 2017)

### Resource Assigner

- Resource Assigner was not handling MSSS Imaging Pipeline correctly due to a typo, causing it to get stuck on PRESCHEDULED.

## LOFAR 2.22.2 (Sep 18th, 2017)

### Ingest

- Fixed bug in getting the PI e-mail.

## LOFAR 2.22.1 (Sep 15th, 2017)

### Ingest

- Ingest sends email to both PI and contact author upon completion
- Files which are not on disk (anymore) are marked as failed in MoM
- Ingest checks whether the disk is mounted when it cannot find a file. 


## LOFAR 2.22 (Sep 11th, 2017)

### Instructions

- An attempt has been made to make swlevel more robust against failing RSP boards. If a RSP-image cannot be loaded onto 
an RSP board, swlevel will execute a 48V reset and retry the load. It will do so twice. This  may lead to longer startup 
times for the MAC software on a station, but at least gives more guarantees to end up with a properly functioning 
station.
 
### General

- The Irish station IE613 has been added as a LOFAR station to the software.

### MoM (deployed 10 Aug 2017)

- [#11028](https://support.astron.nl/lofar_issuetracker/issues/11028): Implement new resource Type Triggers in MoM
- [#11130](https://support.astron.nl/lofar_issuetracker/issues/11130): Make priority and allowtriggers visible in MoM GUI

### SAS

- [#11197](https://support.astron.nl/lofar_issuetracker/issues/11197): Changes to XML Generator and pipelineControl to streamline SLURM parameter propagation.
- Several bugfixes to Resource Assigner and Webscheduler.

### MAC

- [#11022](https://support.astron.nl/lofar_issuetracker/issues/11022): Remove usleep and /sbin/pidof from swlevel
- [#11053](https://support.astron.nl/lofar_issuetracker/issues/11053): Fix memory leak in MAC GCF framework
- [#11074](https://support.astron.nl/lofar_issuetracker/issues/11074): Improve robustness of swlevel to hanging RSP boards part 2
- [#11110](https://support.astron.nl/lofar_issuetracker/issues/11110): Fixed a few Coordinates in StationInfo.dat and remove non-existing stations from the list
- [#11112](https://support.astron.nl/lofar_issuetracker/issues/11112): SoftwareMonitor: Give more starttime to TBB and RSP Driver before changing status 

### Cobalt

- [#5441](https://support.astron.nl/lofar_issuetracker/issues/5441): Cobalt can dump raw RSP data to disk (using parset override).
- [#11017](https://support.astron.nl/lofar_issuetracker/issues/11017): swlevel should not show old observations: lingering pid files are now ignored.
- [#11059](https://support.astron.nl/lofar_issuetracker/issues/11059): Improve COBALT loss logging
- [#11115](https://support.astron.nl/lofar_issuetracker/issues/11115): Add LBA_SPARSE_EVEN/ODD to COBALT delay calibration table.

### Pipelines

- [#10805](https://support.astron.nl/lofar_issuetracker/issues/10805): Apply H5Parm files in ApplyCal
- [#10974](https://support.astron.nl/lofar_issuetracker/issues/10974): Let DPPP recognize the type of numbered steps
- [#11114](https://support.astron.nl/lofar_issuetracker/issues/11114): Gaincal discard stations in the calibration when DATA is not flagged but exactly 0.
- [#10741](https://support.astron.nl/lofar_issuetracker/issues/10741): DPPPE: Read in polynomial spectral shape models and use them for prediction in NDPPP.

### Other

- [#11107](https://support.astron.nl/lofar_issuetracker/issues/11107): Adapt Clean_disk to gzips logfiles and keep them on the systems for 180 days
- [#10977](https://support.astron.nl/lofar_issuetracker/issues/10977): Create timeouts around shell calls of rubidium logger
