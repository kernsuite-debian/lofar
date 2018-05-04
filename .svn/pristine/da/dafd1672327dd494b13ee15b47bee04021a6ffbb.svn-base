# LOFAR Documentation Docker Image {#docker_lofar_documentation}

## General

### Description 

This docker container provides the setup and dependencies necessary to automate the generation of documentation from
source code using Doxygen. It is intended to be used to automate the generation of LOFAR documentation - e.g. as part 
of a Jenkins job.


### Author/Owner

The initial Dockerfile was created by Ruud Beukema <mailto:beukema@astron.nl>.


### Overview

This docker container is not part of the production system, hence it isn't part of the LOFAR architecture. So, no 
diagrams here.

- - - 

## Development


### Analyses

This LOFAR Documentation Docker Image is the result of a series of meetings and dicussions about how to make it easier
to create and keep up-to-date LOFAR documentation, such that it is actually done. Doxygen is used to generate the 
documentation in an automated way from both code and static documentation files (with Markdown syntax).


### Design

The Dockerfile is setup such that it downloads all external dependencies that are not available in the package 
repositories first, followed by packages from the package repository. This is to avoid having to perform these download
steps for every change in the Dockerfile that is related to e.g. the building process.


### Source Code

The Docker file and its dependencies (if their license allows it) can be found in SVN folder:

    Docker/lofar-documentation


### Known issues

#### Bootstrap Theme

As of Doxygen version 1.8.12 Doxygen uses smartmenu's which breaks our Bootstrap Theme (see [this issue]). Therefore 
use Doxygen version 1.8.11 for generating the HTML output (or make the theme work with the newer Doxygen 
version).

[this issue]: https://github.com/Velron/doxygen-bootstrapped/issues/23  "Bootstrap Theme issue"


#### To Do's

@todo Move *package.dox* files to their respective */doc* directory throughout the LOFAR source tree.
@todo Complete/Correct the LOFAR Software Decomposition (the <a href="modules.html">Modules</a> section) by adding *package.dox* files in the appropriate locations
@todo Complete/Add documentation to the LOFAR source tree, copying as much existing documentation from the wiki as possible.


### Testing


### Build & Deploy

For building a docker image from the directory where Dockerfile resides (together with the WinCC_OA folder, read below) 
execute:


    docker build -t lofardocker .


## Usage

This docker container contains no LOFAR source code trunk/branch by itself. One should either check it out from within
the container or inject (mount) a host folder in the image e.g:


    -v [LOFAR branch on host]:/opt/LOFAR/.


The Dockerfile expects that the WinCC_OA packages reside in a WinCC_OA/ folder relative to the Dockerfile (so, in its 
build context).

A hostname should be used by the container which CMake can use to lookup the corresponding variants file (named 
"Cmake/variants/variants.lofar-documentation"). This is done by running the container with the argument:


    -h lofar-documentation


The environment variables listed below (with their default) value can be used to manipulate Doxygen's documentation 
generation. 

 
    DOX_REVISION_SLUG="Unknown Revision"
    DOX_SERVER_BASED_SEARCH=NO


They can be changed by running the container with arguments:


    -e DOX_REVISION_SLUG="Release 2.21 -e DOX_SERVER_BASED_SEARCH=YES"


Complete usage example:
 
    docker run \
        -h lofar-documentation \
        -e DOX_REVISION_SLUG="Release 2.21 \
        -e DOX_SERVER_BASED_SEARCH=YES" \
        -v ~/svn/LOFAR/trunk:/opt/LOFAR/ \
        -lofardocker:latest
