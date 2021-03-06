# Software Documentation

## General

### Introduction

Welcome to the LOFAR Software Documentation, the documentation generated from the 
[LOFAR SVN tree](https://svn.astron.nl/LOFAR/) ([Browser View](https://svn.astron.nl/viewvc/LOFAR/))) using 
[Doxygen](http://www.stack.nl/~dimitri/doxygen/). Its target audience are *Developers*, *Software Support Personnel* 
and *System Administrators*. For *End-User* Documentation and information for *Operators* please refer to the 
[LOFAR-wiki](https://www.astron.nl/lofarwiki).

### Quick Links

- [LOFAR Release Notes](@ref release_notes)


### Doxygen

Refer to the [Doxygen Quick Guide](@ref doxygen_quick_guide) for information on how to write documentation for Doxygen. 
When documenting software components please use and adhere to this 
[Software Documentation Template](@ref sw_documentation_template).


## Architecture

### Top-level

Link to some online top-level diagram of LOFAR generated by the drawing tool chosen from the 
[Drawing Tool Comparison](https://docs.google.com/spreadsheets/d/1JC8zHE7Vx3RyuQWJFAhUd_hUtxQjatORp8V8bYZ3soA/edit?ts=599bc23c#gid=326610509) 
for example [this DrawIO drawing](https://www.draw.io/?state={%22ids%22:[%220B5fohp6auM-uWlVYajlZcTc2SDg%22],%22action%22:%22open%22,%22userId%22:%22102373349346206970364%22}#G0B5fohp6auM-uWlVYajlZcTc2SDg).


### Sub-systems

The LOFAR Software System can be decomposed into several sub-systems:

* CEP
 * Pipelines
  * Pulsar
  * Default Pre Processing Pipeline
  * Inspection Plots Pipeline
  * Adder
* SAS
 * XML Generator
 * OTB
  * Scheduler
 * Resource Assignment
  * Responsive Telescope
  * Dragnet
  * WebScheduler
* MAC
 * Central (CCU)
  * Observation Control
  * MAC Scheduler
 * Station (LCU)
  * Station Control
  * Hardware Monitor
  * Clock Control
  * BeamServer
  * CalibrationServer
  * TBB
  * RSP
  * Station Test
 * WinCC
* MOM (not in this repository)
* LTA
 * Injest
 * Staging (not in this repository)
* Cobalt
* NorthStar (not in this repository)
* RTSM

## Support & Maintenance

Please refer to the 
[Software Support Start Page](https://www.astron.nl/lofarwiki/doku.php?id=engineering:software_support_start) for the
Support schedule, a F.A.Q. and further information on support and maintenance.

### Reporting bugs

LOFAR developers can file their bug reports in the [LOFAR Issue Tracker](https://support.astron.nl/lofar_issuetracker).
Alternatively one can submit a bug report by sending and email to <mailto:softwaresupport@astron.nl>.

Todo's and bugs identified in the source code are listed on their individual pages which are available on the 
<a href="pages.html">Related Pages</a> page.


## Development

### Standards & Procedures

- [Software Documentation Template](@ref sw_documentation_template) (*proposal*)
- [Definition of Done](https://www.astron.nl/lofarwiki/doku.php?id=engineering:software:scrum&s[]=dod)
- Review Checklist
- [Coding Conventions](https://www.astron.nl/lofarwiki/doku.php?id=engineering:software:codingconventions)
- Testing Conventions
- [Software Development Policy](https://www.astron.nl/lofarwiki/doku.php?id=engineering:software:developmentmanagementpolicy)
- [LOFAR Release Procedure](https://www.astron.nl/lofarwiki/doku.php?id=engineering:software:releaseprocedure)
- [Glossary](@ref glossary)

## Usage


### Copyright & Licenses

The copyright of this documentation and all LOFAR source code is owned by [ASTRON](http://www.astron.nl/) unless granted 
otherwise by the applicable license(s) - refer to the [COPYING](https://svn.astron.nl/LOFAR/trunk/COPYING) file for more
information.
