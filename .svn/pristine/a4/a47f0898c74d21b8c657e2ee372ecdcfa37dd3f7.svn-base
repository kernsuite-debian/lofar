# This docker needs a ./LOFAR/ directory with the software stack to build.
#
# For a local mom database, a momdb_init.sql is required. 
# For momqueryservice, a mom.ini has to be present 
# For mom-otdb-adapter, a custom config directory has to be present 
#
# Further, startup.sh as an entry point for the docker
#
#
# Furthermore, a hostname should be used by the container which CMake can use to 
# lookup the corresponding variants file. This is done by running the container 
# with:
# -h lofarbuildandtestdocker
#
#
# The rest interface on port 8000 has to be exposed in order to access it on localhost. 

# Complete usage example:
#
# docker build -t lofarbuildandtestdocker .
# docker run -h lofarbuildandtestdocker -it -p 8000:8000 -p 5672:5672 lofarbuildandtestdocker:latest

# Note: centos/systemd depends on centos7
FROM centos/systemd
MAINTAINER "Joern Kuensemoeller" - This is based on Ruud Beukema's work

RUN systemctl enable dbus.service

# -------------------------------------------------------------------------------------
# Install packages required by Ansible
RUN yum -y install python-yaml python-jinja2 git

# -------------------------------------------------------------------------------------
# Download Ansible and set paths
RUN mkdir -p /opt/ansible
RUN git clone http://github.com/ansible/ansible.git /opt/ansible

ENV PATH /opt/ansible/bin:/sbin:/usr/sbin:/usr/bin
ENV ANSIBLE_LIBRARY /opt/ansible/library
ENV PYTHONPATH /opt/ansible/lib:$PYTHON_PATH

# Place LOFAR stack in Container for RT-Task10875, so ansible can build packages 
COPY LOFAR /opt/LOFAR
COPY conf/momdb_init.sql /
COPY edit_these_files/mom.ini /root/.lofar/dbcredentials/
COPY conf/build.ini /

# Copy Apache configuration files
COPY conf/wsgi.conf /

# Inject Ansible playbook and run it
RUN mkdir -p /etc/ansible
COPY ansible/roles /etc/ansible
COPY ansible/hosts /etc/ansible
COPY ansible/bld.yaml /etc/ansible

RUN ansible-playbook -v /etc/ansible/bld.yaml -c local

# Try to reduce the image size
RUN yum clean all

# Give user SSH and local access (with set locale)
EXPOSE 22 3000
EXPOSE 8000
EXPOSE 5672

# Copy startup script as entry point (sets up queues and starts services)
COPY conf/startup.sh /
CMD /bin/bash /startup.sh
