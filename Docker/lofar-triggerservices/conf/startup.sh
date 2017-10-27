#!/bin/bash

# Create the log directory.
mkdir -p /opt/LOFAR/var/log

echo 'Starting Qpid...' &&
qpidd 2>&1 > /opt/LOFAR/var/log/qpid.log &
sleep 2;

echo 'Setting up queues...' &&
qpid-config add exchange topic devel.lofar.trigger.command &&
qpid-config add exchange topic devel.lofar.trigger.notification &&
qpid-config add exchange topic devel.lofar.ra.command &&
qpid-config add exchange topic devel.lofar.spec.command &&
qpid-config add queue mom.importxml &&
sleep 2;

echo 'Init LOFAR env...';
. /opt/LOFAR/build/gnucxx11_opt/lofarinit.sh &&
sleep 2;

echo 'Starting LOFAR services...' &&
specificationservice 2>&1 > /opt/LOFAR/var/log/specificationservice.log &
specificationvalidationservice 2>&1 > /opt/LOFAR/var/log/specificationvalidationservice.log &
specificationtranslationservice 2>&1 > /opt/LOFAR/var/log/specificationtranslationservice.log &
triggerservice 2>&1 > /opt/LOFAR/var/log/triggerservice.log &

echo 'Starting Postgres...' &&
runuser -l postgres -c '/usr/pgsql-9.6/bin/pg_ctl -D /var/lib/pgsql/9.6/data/ start' &&

echo 'Starting Mysql...' &&
runuser -l mysql -c 'mysqld_safe' &
sleep 5;

cd; momqueryservice -C MoM  2>&1 > /opt/LOFAR/var/log/momqueryservice.log &


postfix start;

echo 'Staring Apache...' &&
/usr/sbin/httpd -k restart

echo  'Have fun!' &&
/bin/bash
