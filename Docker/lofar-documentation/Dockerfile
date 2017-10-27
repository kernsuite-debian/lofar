FROM centos:7
MAINTAINER "Ruud Beukema" <beukema@astron.nl>

# -------------------------------------------------------------------------------------
# Install set of core repositories and tools
# maybe add: rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL xxxxx?

RUN yum -y update && \
    yum -y install \
      epel-release \
      wget && \
    yum clean all

# -------------------------------------------------------------------------------------
# Download source code of 3rd party software projects to /opt/downloads first, so that
# that doesn't need to be repeated when we're iteratively improving the docker

RUN mkdir -p /opt/downloads && \
    cd /opt/downloads && \
    \
    wget -O unittest-cpp-1.6.1.tar.gz https://github.com/unittest-cpp/unittest-cpp/archive/v1.6.1.tar.gz && \
    wget -O blitz-0.10.tar.gz http://downloads.sourceforge.net/project/blitz/blitz/Blitz%2B%2B%200.10/blitz-0.10.tar.gz && \
    wget -O casacore-2.1.0.tar.gz https://github.com/casacore/casacore/archive/v2.1.0.tar.gz && \
    wget -O casarest-1.4.2.tar.gz https://github.com/casacore/casarest/archive/v1.4.2.tar.gz && \
    wget -O aoflagger-2.9.0.tar.bz2 https://sourceforge.net/projects/aoflagger/files/aoflagger-2.9.0/aoflagger-2.9.0.tar.bz2/download && \
    wget -O PyBDSF-1.8.9.tar.gz https://github.com/lofar-astron/PyBDSF/archive/v1.8.9.tar.gz && \
    wget -O DAL-master.tar.gz https://github.com/nextgen-astrodata/DAL/archive/master.tar.gz && \
    wget -O WSRT_Measures.ztar --ftp-user=anonymous ftp://ftp.astron.nl/outgoing/Measures/WSRT_Measures.ztar && \
    wget -O cuda.rpm https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda-repo-rhel7-8-0-local-ga2-8.0.61-1.x86_64-rpm && \
    wget -O plantuml.jar https://sourceforge.net/projects/plantuml/files/plantuml.jar/download && \
    wget -O doxygen-1.8.11.tar.gz https://sourceforge.net/projects/doxygen/files/rel-1.8.11/doxygen-1.8.11.src.tar.gz/download

# -------------------------------------------------------------------------------------
# Copy in the WinCC_OA packages
COPY WinCC_OA/* /opt/downloads/

# -------------------------------------------------------------------------------------
# Install yum packages

RUN rpm --import https://dev.monetdb.org/downloads/MonetDB-GPG-KEY && \
    yum install -y https://dev.monetdb.org/downloads/epel/MonetDB-release-epel.noarch.rpm && \    
    \
    yum install -y --nogpgcheck /opt/downloads/WinCC_OA_3.14-base-rhel-0-4.x86_64.rpm && \
    yum install -y --nogpgcheck /opt/downloads/WinCC_OA_3.14-applications-rhel-0-4.x86_64.rpm && \
    yum install -y --nogpgcheck /opt/downloads/WinCC_OA_3.14-help-en-rhel-0-4.x86_64.rpm && \
    yum install -y --nogpgcheck /opt/downloads/WinCC_OA_3.14-specialfunctions-rhel-0-4.x86_64.rpm && \
    \
    yum install -y \
    atop \
    autoconf \
    autogen \
    armadillo-devel \
    bison \
    bison \
    blas \
    blas-devel \
    boost \
    boost-devel \
    boost-python \
    bzip2 \
    cfitsio \
    cfitsio-devel \
    cmake \
    cmake-gui \
    dkms \
    docker \
    dvips \
    fabric \
    fftw \
    fftw-devel \
    flex \
    gcc-c++ \
    gcc-gfortran \
    gettext \
    ghostscript \
    git \
    graphviz \
    grub2 \
    gs \
    gsl-devel \
    gtkmm24-devel \
    gtkmm30-devel \
    hdf5 \
    hdf5-devel \
    hdparm \
    java-1.8.0-openjdk-devel \
    kernel-devel \
    kernel-headers \
    lapack \
    lapack-devel \
    libpng-devel \
    libpqxx-devel \
    libvdpau-devel \
    libxml++-devel \
    log4cplus-devel \
    make \
    mariadb \
    mariadb-server \
    mpich \
    mpich-3.0-devel \
    mysql-connector-python \
    nano \
    ncurses \
    ncurses-devel \
    ntp \
    numpy \
    numpy-f2py \
    numactl-devel \
    openblas-devel \
    opencl-headers \
    openmpi \
    openmpi-devel \
    postfix \
    pyfits \
    python2-mock \
    python-devel \
    python-ldap \
    python-lxml \
    python-matplotlib \
    python-pip \
    python-psycopg2 \
    python-qpid \
    python-sphinx \
    python-testing.postgresql \
    qpid-cpp-server \
    qpid-cpp-server-linearstore \
    qpid-cpp-client \
    qpid-tools  \
    qpid-cpp-client-devel \
    qt-devel \
    readline \
    readline-devel \
    scipy \
    swig \
    texlive-collection-latexrecommended \
    valgrind-devel \
    wcslib \
    wcslib-devel \
    xterm \
    ypbind \
    yp-tools \
    zabbix22-agent && \
    \
    yum clean all

# -------------------------------------------------------------------------------------
# Install Python packages through (the latest) pip

RUN pip install --upgrade pip && \
    pip --no-cache-dir install \
    django \
    djangorestframework \
    djangorestframework-xml \
    doxypypy \
    pymonetdb \
    python-monetdb \
    testing.mysqld \
    xmljson \
    xmlrunner

# -------------------------------------------------------------------------------------
# Download, Extract, build and install the downloaded 3rd party dependencies

RUN tar -xzvf /opt/downloads/unittest-cpp-1.6.1.tar.gz -C /opt && \
    cd /opt/unittest-cpp-1.6.1 && \
    cmake . && \
    make -j4 && \
    make install && \
    \
    tar xzvf /opt/downloads/blitz-0.10.tar.gz -C /opt && \
    cd /opt/blitz-0.10 && \
    ./configure && \
    make lib install && \
    \
    mkdir -p /usr/share/casacore/data && \
    tar -xzf /opt/downloads/WSRT_Measures.ztar -C /usr/share/casacore/data && \
    \
    mkdir -p /opt/casacore-2.1.0/build && \
    tar -xzf /opt/downloads/casacore-2.1.0.tar.gz -C /opt/casacore-2.1.0 && \
    cd /opt/casacore-2.1.0/build && \
    cmake \
        -DDATA_DIR=/usr/share/casacore/data \
        -DUSE_FFTW3=ON \
        -DBUILD_PYTHON=ON  \
        -DUSE_THREADS=ON \
        -DCXX11=ON \
        -DUSE_OPENMP=ON \
        -DCMAKE_INSTALL_PREFIX=/opt/casacore-2.1.0 \
        -DUSE_HDF5=ON \
        ../casacore-2.1.0 && \
    make -j4 && \
    make install && \
    ln -s /opt/casacore-2.1.0 /opt/casacore && \
    \
    mkdir -p /opt/casarest-1.4.2/build && \
    tar -xzf /opt/downloads/casarest-1.4.2.tar.gz -C /opt/casarest-1.4.2 && \    
    cd /opt/casarest-1.4.2/build && \
    cmake \
        -DDATA_DIR=/usr/share/casacore/data \
        -DUSE_FFTW3=ON  \
        -DBUILD_PYTHON=ON \
        -DUSE_THREADS=ON \
        -DCXX11=ON \
        -DCMAKE_INSTALL_PREFIX=/opt/casarest-1.4.2 \
        -DCASACORE_ROOT_DIR=/opt/casacore \
        -DCFITSIO_INCLUDE_DIR=/usr/include/cfitsio \
        ../casarest-1.4.2 && \
    make -j4  && \
    make install && \
    ln -s /opt/casarest-1.4.2 /opt/casarest && \
    \
    mkdir -p /opt/aoflagger-2.9.0/build && \
    tar -xjf /opt/downloads/aoflagger-2.9.0.tar.bz2 -C /opt/aoflagger-2.9.0 && \    
    cd /opt/aoflagger-2.9.0/build && \
    cmake \
        -DCASACORE_ROOT_DIR=/opt/casacore \
        -DCMAKE_PREFIX_PATH=/opt/casacore/builds/casacore-2.3.0/build/gnucxx11_opt \
        -DCMAKE_INSTALL_PREFIX=./ \
       ../aoflagger-2.9.0 && \
    make -j4  && \
    make install  && \
    \
    mkdir -p /opt/pybdsf-1.8.9/PyBDSF-1.8.9/lib64/python2.7/site-packages && \
    tar -xzf /opt/downloads/PyBDSF-1.8.9.tar.gz -C /opt/pybdsf-1.8.9 && \    
    export PYTHONPATH=/opt/pybdsf-1.8.9/PyBDSF-1.8.9/lib64/python2.7/site-packages:$PYTHONPATH && \
    cd /opt/pybdsf-1.8.9/PyBDSF-1.8.9  && \
    python setup.py install --prefix=/opt/pybdsf-1.8.9/PyBDSF-1.8.9 && \
    \
    mkdir -p /opt/dal/DAL-master/build && \
    tar -xzf /opt/downloads/DAL-master.tar.gz -C /opt/dal && \    
    cd /opt/dal/DAL-master/build && \
    cmake ../ -DCMAKE_INSTALL_PREFIX=`pwd` && \
    make -j4 && \
    make install && \
    \
    rpm -i /opt/downloads/cuda.rpm && \
    yum install -y cuda && \
    \
    mkdir /opt/plantuml && \
    mv /opt/downloads/plantuml.jar /opt/plantuml && \
    \
    tar -xzf /opt/downloads/doxygen-1.8.11.tar.gz -C /opt/downloads && \
    mkdir -p /opt/downloads/doxygen-1.8.11/build  && \
    cd /opt/downloads/doxygen-1.8.11/build  && \
    cmake -G "Unix Makefiles" .. && \
    make -j4 && \
    make install && \
    \
    rm -rf /opt/downloads

# Paths that need to be permanently added to some environment variable should be set using the 
# Docker ENV command
ENV PYTHONPATH /opt/pybdsf-1.8.9/PyBDSF-1.8.9/lib64/python2.7/site-packages:$PYTHONPATH
ENV PATH /usr/local/cuda-8.0/bin:$PATH
ENV DOX_SERVER_BASED_SEARCH NO
ENV DOX_REVISION_SLUG "Unknown revision"

# -------------------------------------------------------------------------------------
# Make the documentation build script accessible within Docker
COPY build_documentation.sh /usr/bin

# -------------------------------------------------------------------------------------
# Generate documentation
ENTRYPOINT ["build_documentation.sh"]
#CMD ["/bin/bash"]
