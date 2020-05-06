#!/bin/bash -x

# -----------------------------------------
#   Configuration
# -----------------------------------------

# Whether to modify production (true) or test (false)
if [ "$LOFARENV" == "PRODUCTION" ]; then
  PROD=true
  PREFIX=
elif [ "$LOFARENV" == "TEST" ]; then
  PROD=false
  PREFIX="test."
else
  PROD=false
  PREFIX="devel."
fi


# Host names to use
if $PROD; then
  echo "----------------------------------------------"
  echo "Populating database for PRODUCTION environment"
  echo ""
  echo "Press ENTER to continue, or ^C to abort"
  echo "----------------------------------------------"
  read

  CCU=ccu001.control.lofar
  MCU=mcu001.control.lofar
  SCU=scu001.control.lofar

  MOM_SYSTEM=lcs023.control.lofar
  MOM_INGEST=lcs029.control.lofar
else
  CCU=ccu199.control.lofar
  MCU=mcu199.control.lofar
  SCU=scu199.control.lofar

  MOM_SYSTEM=lcs028.control.lofar
  MOM_INGEST=lcs028.control.lofar
fi

# MessageBus
qpid-config -b $CCU add queue ${PREFIX}mac.task.feedback.state --durable
qpid-config -b $MCU add queue ${PREFIX}otdb.task.feedback.dataproducts --durable
qpid-config -b $MCU add queue ${PREFIX}otdb.task.feedback.processing --durable
qpid-config -b $MCU add queue ${PREFIX}lofar.task.specification.system --durable
qpid-config -b $CCU add queue ${PREFIX}lofar.task.specification.system --durable
qpid-config -b $CCU add queue ${PREFIX}mom.task.specification.system --durable
qpid-config -b $MOM_SYSTEM add queue ${PREFIX}mom.task.specification.system --durable
qpid-config -b $CCU add queue mom.command --durable
qpid-config -b $MOM_SYSTEM add queue mom.command --durable
qpid-config -b $CCU add queue mom.importxml --durable
qpid-config -b $MOM_SYSTEM add queue mom.importxml --durable
qpid-config -b $MOM_SYSTEM add queue ${PREFIX}mom.task.feedback.dataproducts --durable
qpid-config -b $MOM_SYSTEM add queue ${PREFIX}mom.task.feedback.processing --durable
qpid-config -b $MOM_SYSTEM add queue mom-otdb-adapter.importxml --durable
qpid-config -b $CCU add queue mom-otdb-adapter.importxml --durable
qpid-route -d route add $MOM_SYSTEM $CCU mom-otdb-adapter.importxml '#'
qpid-config -b $MOM_SYSTEM add exchange topic ${PREFIX}lofar.mom.bus --durable
qpid-config -b $MOM_INGEST add exchange topic ${PREFIX}lofar.mom.bus --durable
qpid-config -b $MOM_SYSTEM add exchange topic ${PREFIX}lofar.mom.command --durable
qpid-config -b $MOM_SYSTEM add exchange topic ${PREFIX}lofar.mom.notification --durable
qpid-config -b $SCU add exchange topic ${PREFIX}lofar.mom.bus --durable
qpid-config -b $SCU add exchange topic ${PREFIX}lofar.mom.command --durable
qpid-config -b $SCU add exchange topic ${PREFIX}lofar.mom.notification --durable
qpid-route -d route del $MOM_SYSTEM $SCU ${PREFIX}lofar.mom.bus '#'
qpid-route -d dynamic del $MOM_SYSTEM $SCU ${PREFIX}lofar.mom.bus
qpid-route -d route add $MOM_SYSTEM $SCU ${PREFIX}lofar.mom.bus '#'
qpid-route -d route del $MOM_SYSTEM $SCU ${PREFIX}lofar.mom.command '#'
qpid-route -d dynamic del $MOM_SYSTEM $SCU ${PREFIX}lofar.mom.command
qpid-route -d route add $MOM_SYSTEM $SCU ${PREFIX}lofar.mom.command '#'
qpid-route -d route del $SCU $MOM_SYSTEM ${PREFIX}lofar.mom.notification '#'
qpid-route -d dynamic del $SCU $MOM_SYSTEM ${PREFIX}lofar.mom.notification
qpid-route -d route add $SCU $MOM_SYSTEM ${PREFIX}lofar.mom.notification '#'
qpid-route -d queue del $CCU $MCU '' '${PREFIX}lofar.task.specification.system'
qpid-route -d queue add $CCU $MCU '' '${PREFIX}lofar.task.specification.system'
qpid-route -d queue del $MOM_SYSTEM $CCU '' '${PREFIX}mom.task.specification.system'
qpid-route -d queue add $MOM_SYSTEM $CCU '' '${PREFIX}mom.task.specification.system'
qpid-route -d queue del $MOM_SYSTEM $CCU '' 'mom.command'
qpid-route -d queue add $MOM_SYSTEM $CCU '' 'mom.command'
qpid-route -d queue del $MOM_SYSTEM $CCU '' 'mom.importxml'
qpid-route -d queue add $MOM_SYSTEM $CCU '' 'mom.importxml'
qpid-route -d queue del $CCU $MOM_SYSTEM '' 'mom-otdb-adapter.importxml'
qpid-route -d queue add $CCU $MOM_SYSTEM '' 'mom-otdb-adapter.importxml'

# Messaging (to JAVA)
qpid-config -b $SCU add queue mom.importxml --durable
qpid-route -d queue del $MOM_SYSTEM $SCU '' 'mom.importxml'
qpid-route -d queue add $MOM_SYSTEM $SCU '' 'mom.importxml'

# Messaging

# Strategy:
#   - 1 exchange ("lofar", possibly prefixed with "test." or "devel.")
#   - 1 broker (scu001/scu099/localhost)
#   - each notification listener creates its own temp/permanent queue on the relevant exchange ("lofar.notification.for.XXXX")
#   - each RPC server creates its own temp/permanent queue on the relevant exchange ("lofar.command.XXXX")
#   - both setup bindings to forward the right messages to their queue

ssh $SCU rabbitmqadmin declare exchange name=lofar.command type=topic
