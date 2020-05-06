# LOFAR Glossary of Terms and Abbreviations {#glossary} 

## Introduction

### Purpose of this document
This glossary is intended to facilitate the discussions within the LOFAR project by providing unambiguous definitions 
of terms and abbreviations.
In principle, all LOFAR documentation shall refer to this glossary.

### Executive summary
This document provides a definition of abbreviations and terms to be used in the LOFAR project. Several documents 
produced so far contain glossaries that have been taken as input. Other sources are general standards like ECSS and ISO.

### Author/Owner
Adriaan Renting <renting@astron.nl>

## Glossary of Abbreviations

| Abbreviation | Context | Meaning |
| --- | --- | --- |
| ACC | CEP | Application Configuration and Control |
| AD | LOFAR | Applicable Document |
| ADD | LOFAR | Architectural Design Document |
| ADC | | Analog Digital Conversion |
| AGN | Science | Active Galactic Nucleus |
| AGP | | Accelerated Graphical Port |
| AIPS | Software | Astronomical Information Processing System or classical AIPS |
| AIPS++ | Software | The AIPS++ project was a project from the nineties supposed to replace the original Astronomical Information Processing System or classical AIPS. The ++ comes from it being mainly developed in C++. It’s also known as AIPS 2. It evolved into CASA, casacore and casarest (see those entries).|
| AIT | LOFAR | Assembly,  Integration and Test |
| API | Software | Application Programming Interface |
| ARG | MAC | Array Receptor Group |
| ARVI | LOFAR | Archiving Virtual Instrument |
| AUX | LOFAR | Auxillary |
| Az | Coordinates | Azimuth |
| Beam | | Do not use Beam, use one of the specific beams, like Station Beam, Tile Beam, Antenna Beam |
| - | | A beam is formed by combining all the SubArrayPointing, one for each station, which are looking in a particular direction. There may be more than one beam for each SubArrayPointing, and different types of beams are available. |
| BF | LOFAR | Beam-Formed data. Used for time-series data recorded in LOFAR Tied Array Mode, even though Interferometry data is also "beam formed". |
| BBI | CEP | Black Board Imager. (Never implemented ?) |
| BBS | CEP | Black Board Selfcal, calibration application used for LOFAR imaging data. |
| BBTN | LOFAR | Black Board Transport Network (never used?) |
| BG | CEP | Blue Gene - IBM supercomputers used by LOFAR 2007-2014 |
| BG/L | CEP | Blue Gene/ L - series |
| BG/P | CEP | Blue Gene/ P - series |
| BSR | Calibration | Band-pass Saw-tooth Ripple |
| CASA | Software | The Common Astronomy Software Applications package. User software for radioastronomy devel- oped out of the old AIPS++ project. The project is led by NRAO with contributions from ESO, CSIRO/ATNF, NAOJ and ASTRON. [?] |
| casacore | Software | The set of C++ libraries that form the basis of CASA and several other astronomical packages. It contains classes for storing and handling visibility and image data, RDBMS-like table system and handling coordinates. Mainly maintained by ASTRON and CSIRO/ATNF. [?] |
| casarest | Software | The libraries and tools from the old AIPS++ project that are not part of casacore or CASA but still in use. |
| CCB | - | Configuration Change Board |
| CCP | - | Change Control Procedure |
| CDR | - | Critical Design Review |
| CEP | LOFAR | Central Processing facility. |
| Channel | | The subband data of a LOFAR observation may be passed through a second polyphase filter to obtain a large number of channels (i.e. to increase the spectral resolution). |
| CI | LOFAR | Configuration Item |
| CIA | LOFAR | Common Interface Application Sub-system |
| CLA  | Data Formats | Common LOFAR attributes. Set of root-level attributes that are used and required as attributes in all LOFAR science data products. If a value is not available for an Attribute, ‘NULL’ maybe used. |
| Co-I | LOFAR | Co-investigators on an observation project under the leadership of the PI. |
| COTS | - | Common Off-the-shelf |
| CRC | - | Cyclic Redundancy Check |
| CS | LOFAR | Core Station. LOFAR Station within ~15 km of the Superterp with 2 small HBA fields. |
| CS1 | LOFAR | Core Station One, test station with pre-production hardware (2007) |
| CS??? | LOFAR | LOFAR Core Station ??? |
| CWDM | WAN | Coarse Wave Division Multiplexing |
| DAS | CEP | Direct Attachment Storage |
| Data Interface | | Set of definitions that describe the contents and structure of data files. |
| Data Access Layer (DAL) | | A C++ library with Python bindings providing read/write functionality for HDF5 format files, as well as access to Measurement Sets. |
| DBD | Station | Digital Board Design |
| DCR | - | Document Change Request |
| DDP | LOFAR | Data Delivery Package |
| DDV | LOFAR | Design, Development and Verification | 
| Dec | Coordinates | Declination |
| DFT | - | Discrete Fourier Transform |
| D-GPS | Coordinates | Differential Global Positioning System |
| DOA | Station | Direction Of Arrival |
| DPPP | CEP | Default Pre-Processing Pipeline, pipeline used for LOFAR imaging data |
| DTN | ? | Data Transport Network |
| DWDM | WAN | Dense Wavelength Division Multiplexing |
| EAS | Science | Extensive Air-Shower |
| El | Coordinates | Elevation |
| EMC | - | Electro-Magnetic Compatibility |
| EMI | - | Electro-Magnetic Interference |
| EMP | - | Electro-Magnetic Pulse |
| EoR | Science | Epoch of Reionization |
| EoR | LOFAR | Epoch of Reionization Key Science Project |
| EPA | Station | Embedded Processing Application |
| EPDM | LBA | Ethylene Propylene Diene Monomer (kind of rubber) |
| EPROM | - | Erasable Programmable Read Only Memory |
| ESD | - | Electro-Static Discharge |
| FDIR | SHM | Fault Detection, Isolation and Recovery |
| FIR | - | Finite Impulse Response |
| FITS | Data Formats | FITS (Flexible Image Transport System) is a digital file format used to store, transmit, and manipulate scientific and other images. FITS is commonly used in astronomy. |
| FMECA | ? | Failure Mode Effects and Criticality Analysis |
| FoV | Science | Field of View. |
| FPP | Station | Flexible Poly Popylene |
| FPGA | - | Field Programmable Gate Array |
| FSI | CEP | Flagger, Selfcal, Imager |
| FTS | Station | Full Test Station |
| GbE | - | Gigabit Ethernet |
| GCF | MAC | Generic Control Network |
| GPS | Coordinates | Global Positioning System |
| GPU | - | Graphical Processor Unit |
| GSM | Science | Global Sky Model. Used in calibration. |
| H/W | -  | Hardware |
| HBA | LOFAR | High Band Antenna. 120-250 MHz dipoles stored in a styrofoam "tile". |
| HDFView | Software | Hierarchical Data Format Viewer; a Java software tool for viewing the HDF5 structure and data. [http://www.hdfgroup.org/hdf-java-html/hdfview/] |
| HDF5 | Data Formats | Hierarchical Data Format, version 5 [?]. A file format capable of accommodating large datasets that com- prises two (2) primary types of objects: groups and datasets. Implements self-organisation and hier- archical structures within the file format itself, facilitating self-contained data administration. [?, ?] |
| HDF5 group | Data Formats | A grouping structure containing zero or more HDF5 objects, together with supporting meta- data. |
| HDF5 | Data Formats | dataset A multidimensional array of data elements, together with supporting meta-data. |
| HDU | Data Formats | Header-Data Unit Though typically used for FITS data descriptions, the term “HDU” can also be used more generically when discussing any data group that contains both data and a descriptive header. |
| HMI | - | Human Machine Interface |
| Hypercube | Science | The hypercube is a generalization of a 3-cube to n dimensions, also called an n-cube or measure polytope. In data modelling a hypercube is a cube-like logical model in which all measurements are organized into a multidimensional space. |
| ICD | - | Interface Control Document |
| ICS | MAC | Interface Control System |
| ICWG | LOFAR | Interface Control Working Group |
| IOC | LOFAR | Initial Operations Capability |
| IS-FR? | Station | International Station France number ? (not used any more) |
| IS-GE? | Station | International Station Germany number ? (not used any more) |
| IS-IT? | Station | International Station Italy number ? (not used any more) |
| IS-SW? | Station | International Station Sweden number ? (not used any more) |
| IS-UK? | Station | International Station United Kingdom number ? (not used any more) |
| ITS | LOFAR | Initial Test Station |
| IVOA | - | International Virtual Observatory Alliance |
| JLOC | LOFAR | Joint LOFAR Operations Centre |
| JTAG | - | Joint Test Action Group of IEEE |
| JTB | Station | JTAG Test Board |
| KSP | LOFAR | Key Science Project. One of several major observational and research projects defined by the LOFAR organization. These Key Science Projects are,- Cosmic Magnetism in the Nearby Universe-  High Energy Cosmic Rays- Epoch of Re-ionization- Extragalactic Sky Surveys- Transients - Pulsars, Jet Sources, Planets, Flare stars-  Solar Physics and Space Weather |
| KTV | SAS/MAC | Key Time-Value |
| LAN | - | Local Area Network |
| LBA | LOFAR | Low Band Antenna. 10-80 MHz tetrahedron dipoles |
| LBL | Station | Low Band Low |
| LBH | Station | Low Band High |
| LCU | Station/MAC | Local Control Unit |
| LOFAR | LOFAR | The LOw Frequency ARray. LOFAR is a multipurpose sensor array; its main application is astronomy at low radio frequencies, but it also has geophysical and agricultural applications. [http://www.lofar.org/] |
| LOFAR Sky Image | | Standard LOFAR Image Cube. A LOFAR data product encompassing science data, associated meta-data, and associated calibration information, including a Local Sky Model (LSM) , and other ancillary meta groups that are defined in this document. |
| LR | LOFAR | LOFAR Receiver (might not be used any more?) |
| LRU | ? | Line Replaceable Unit |
| LS | ? | LOFAR Scheduler |
| LSM/GSM | Science| The Local Sky Model/Global Sky Model. Sky Models are essentially catalogues of known real radio sources in the sky. A Local Sky Model for an observation is merely a subset of a Global Sky Model catalogue pertaining to that observation’s relevant region of the sky. Used in calibration. |
| LTA | LOFAR | The Long Term Archive for LOFAR. |
| LVDS | Station | Low Voltage Differential Signalling |
| MAC | LOFAR | Monitoring And Control sub-system |
| MACN | WAN | Monitoring and Control Network |
| MAIT| -  | Manufacturing, Assembly, Integration and Test |
| MCU | MAC | Main Control Unit |
| ME | Science | Measurement Equation. See Hamaker-Bregman-Sault |
| MEP | CEP | Measurement Equation Processing (Database) (not used any more) |
| MEP | MAC | MAC-EPA Protocol |
| Meq | Science | Measurement Equation. See ME |
| MIM | Science | Minimum Ionospheric Model |
| MIT | - | Massachusetts Institute of Technology |
| MJD | - | Modified Julian Day. Derived from Julian Date (JD) by MJD = JD - 2400000.5. Starts from midnight rather than noon. |
| MPI| - | Message Passing Interface |
| MS | Data Formats | Measurement Set, a self-described, structured set of casacore tables comprising the data and meta-data of an observation. [?] |
| MTBF | - |Mean Time Between Failure |
| MTTR | - | Mean Time To Repair |
| NAA | LOFAR | Non-Astronomical Applications |
| NAS | - | Network Attached Storage |
| NCR | - | Non-Conformance Report |
| NMS | WAN/MAC | Network Management System |
| NRB| - | Non-Conformance Review Board |
| NREN | WAN | National Research and Education Network |
| NRL | - | Naval Research Laboratory |
| OCS | SAS/MAC | Observation Control System |
| OFVI | SAS/MAC | Off-line Virtual Instrument |
| OLAP | CEP | On-line Application Processing. The applications that run on (near) real-time data before it is written to permanent storage |
| ONVI | SAS/MAC | On-line Virtual Instrument |
| OPS | LOFAR | Operations |
| OTDB | SAS/MAC | Observation Tree Database |
| PA | - | Product Assurance |
| PA | MAC | Property Agent |
| PAD | - | Part Approval Document |
| PBL | - | Product Baseline |
| PC | - | Project Control |
| PCB | - | Printed Circuit Board |
| PDP | - | Planning Data Package |
| PDR | - | Preliminary Design Review |
| PDU | - | Power Distribution Unit |
| PI | LOFAR | A Principal Investigator is the lead scientist resopnsible for a particular observation project. |
| PIC | SAS | Physical Instrument Configuration |
| PML | MAC | Property Management Layer |
| PO | - | Purchase Order |
| PPL | - | Preferred Parts List |
| PPM | - | Parts Per Million |
| PPS | - | Pulses Per Second |
| PRBS | Station | Speudo Random Bit Sequence |
| PROM | - | Programmable Read Only Memory |
| PRR | - | Production Readiness Review |
| PSD | - | Power Spectral Density |
| PSF | Science | Point Spread Function. How a single point source is imaged by the instrument |
| PSS | - | Procedures, Standards and Specification |
| PT | - | Product Tree |
| PTR | - | Post Test Review |
| PU | - | Principal User |
| PULP | CEP | Pulsar Pipeline |
| PVD | CEP | Patch Visibilities Database (no longer used?) |
| PVSS | LOFAR | Prozess Visualisierungs und Steuerungs System, now WinCC |
| PWM | - | Pulse Width Modulation |
| PWR | - | Power |
| QA | - | Quality Assurance |
| QBL | - | Qualification Baseline |
| QCI | - | Quality Conformance Inspection |
| QPL | - | Quality Parts List |
| R&D | - | Research and Development |
| RA | Coordinates | Right Ascension |
| Rb | Station | Rubidium (clock) |
| RAID | CEP | Redundant Array of Independent Disks |
| RAMS | - | Reliability, Availability, Maintainability and Safety |
| RCOF | - | Root Cause of Failure |
| RCU | Station | ReCeiver Unit |
| RD | - | Reference Document |
| RE/RS | - | Radiated Emission and Radiated Susceptibility |
| RFA | - | Request for Approval |
| RFD | - | Request for Deviation |
| RFI | ? | Radio Frequency Interference |
| RFQ | - | Request for Quotation |
| RFW | - | Request for Waiver |
| RID | - | Review Item Discrepancy |
| RID | ? | Residual Images Database (no longer used?) |
| RM | Science | Rotation Measure |
| RMSC | Data Formats | The Rotation Measure synthesis cube is a data product which contains the output of LOFAR RM synthesis routines, namely the polarized emission as a function of Faraday depth. As with the Sky Image data files, all associated information is stored within an RMSC file. |
| ROM | - | Read Only Memory |
| ROM | - | Rounding Order of Magnitude |
| RS | LOFAR | Remote Station. LOFAR Station outside ~15 km of the Superterp with 1 HBA field. |
| RS??? | LOFAR | LOFAR Remote Station number ??? |
| RSP | Station | Remote Station Processing Board |
| RTM | ? | Radiative Transfer Model |
| RVD | ? | Residual Visibilities Database (no longer used ?) |
| RVT | - | Radiation Verified Testing |
| SAP | LOFAR | See SubArrayPointing |
| SAS | LOFAR | Specification, Administration and Scheduling |
| SBF | MAC? | Station Beam-former |
| SCADA | - | Supervisory Control and Data Aquisition |
| SCO | Station | Station Control Oscillator |
| SCOE | - | System Check-Out Equipment |
| SCS | LOFAR | Station - Core Selfcal ??? |
| SCV | LOFAR | Station - Core Visibilities ??? |
| SDP | CEP/MAC? | Station Digital Processing |
| SER | - | System Engineering Report |
| SERDES | - | Serializer/Deserializer |
| SFP | WAN | Small Form-Factor Plugable |
| SHM | MAC | system Health Management |
| SIP | CEP | Standard Imaging Pipeline |
| SIP | LTA | Submission Information Package according to OASIS standard model |
| SMP | - |  Simple Message Protocol |
| SNMP | - | Simple Network Management Protocol |
| S/N | - | Signal to Noise ratio |
| SNR | - | Signal to Noise Ratio |
| SOC | LOFAR | Science Operations Centre |
| SOE | - | Sequence Of Events |
| SPR | - | Software Problem Report |
| SPU | Station | Sub-rack Power Unit |
| SRD | - | Software Requirements Document |
| SRG | Mac | Station Receptor Group |
| SRS | LOFAR | System Requirements Specification |
| SSS | LOFAR | Station-Station Selfcal |
| SSV | LOFAR | Station-Station Visibilities |
| ST | - | Short Term |
| Station | LOFAR | Group of antennae separated from other groups. |
| STS | MAC | STation Subsystem |
| SubArrayPointing | | This corresponds to the beam formed by the sum of all of the elements of a station. For any given observation there may be more than one SubArrayPointing, and they can be pointed at different locations. Subband At the station level, LOFAR data are passed through a polyphase filter, producing subbands of either 156.250 kHz or 195.3125 kHz (depending on system settings). |
| SW | - | Software |
| TAI | - | International Atomic Time (Temps Atomique International), atomic coordinate time standard. |
| TBB | Station | Transient Buffer Board |
| TBC | - | To Be Confirmed |
| TBD | - | To Be Determined |
| TBS | - | To Be Specified |
| TBW | - | To Be Written |
| TD | Station | Time Distribution |
| TDB | Station | Time Distribution Board |
| TDS | Station | Time Distribution system |
| TID | Science | Travelling Ionospheric Disturbances |
| TOP | CEP? | Theoretical Operation |
| TP | - | Twisted Pair |
| TPM | - | Technical Performance Measurement |
| TR | - | Test Review |
| TRAP | CEP | Transients Pipeline |
| TRR | - | Test Readiness Review |
| TRRB | - | Test Readiness Review Board |
| TSP |- | Twisted and Shielded Pair |
| UCE | - | Unit Check-out Equipment |
| UML | - | Unified Modelling Language |
| UOC | LOFAR | Ultimate Operations Capability |
| URD | - | User Requirements Document |
| USG | LOFAR | LOFAR User Software Group |
| UTC | - | Coordinated Universal Time (UTC) is a time standard based on International Atomic Time (TAI) with leap seconds added at irregular intervals to compensate for the Earth’s slowing rotation. |
| UTE | - | Unit Test Equipment |
| UUT | - | Unit Under Test |
| UV-Coverage | Science | A spatial frequency domain area that must be covered completely by observation in order to assure an optimal target image (Full UV- Coverage). During observation, the radio telescope turns with respect to its target, due to the earth rotation. A certain -instrument geometry dependent- rotation angle has to be covered in order to accomplish full coverage. |
| VCD | - | Verification Control Document |
| VHECR | | Very High-Energy Cosmic Ray |
| VIC | SAS | Virtual Intrument Configuration |
| VLAN | - | Virtual Local Area Network |
| WAN | - | Wide Area Network |
| WBS | - | Work Breakdown Structure |
| WCS | | World Coordinate Information/System (WCS). The FITS ”World Coordinate System” (WCS) convention defines keywords and usage that provide for the description of astronomical coordinate systems in a FITS image header [?, ?, ?]. also used in other formats. |
| WHAT | LOFAR | Westerbork HBA Antenna Test |
| WinCC | LOFAR | SCADA system by Siemens, formerly PVSS |
| WP | - | Work Package |

## Glossary of Terms



### Note
Based on the following documents:
- LOFAR-ASTRON-RPT-002 v3 (2007): LOFAR Glossary of Terms and Abbreviations
- ICD Glossary

