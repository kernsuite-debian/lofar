#!/bin/bash
#
# To DB first, wipe, use
#
# psql -U postgres -h sasdb --dbname=qpidinfra --file=$LOFARROOT/share/qpidinfrastructure/sql/qpidinfradb.sql
#


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
  LEXAR=lexar003.offline.lofar

  MOM_SYSTEM=lcs023.control.lofar
  MOM_INGEST=lcs029.control.lofar
else
  CCU=ccu199.control.lofar
  MCU=mcu199.control.lofar
  SCU=scu199.control.lofar
  LEXAR=lexar004.offline.lofar

  MOM_SYSTEM=lcs028.control.lofar
  MOM_INGEST=lcs028.control.lofar
fi


# -----------------------------------------
#   Cobalt DataTapping (piggy-backing)
# -----------------------------------------

addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.datatap.command  # COBALT piggy-backing request-reply
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.datatap.notification  # notification who has been granted COBALT piggy-backing

# -----------------------------------------
#   MessageRouter -> MoM
# -----------------------------------------

#addtoQPIDDB.py --broker $CCU --queue ${PREFIX}mom.task.feedback.dataproducts --federation $MOM_SYSTEM
#addtoQPIDDB.py --broker $CCU --queue ${PREFIX}mom.task.feedback.processing --federation $MOM_SYSTEM
#addtoQPIDDB.py --broker $CCU --queue ${PREFIX}mom.task.feedback.state --federation $MOM_SYSTEM

# -----------------------------------------
#   Feedback COBALT/CEP4 -> MAC
# -----------------------------------------
addtoQPIDDB.py --broker $CCU --queue ${PREFIX}mac.task.feedback.state
addtoQPIDDB.py --broker $MCU --queue ${PREFIX}otdb.task.feedback.dataproducts
addtoQPIDDB.py --broker $MCU --queue ${PREFIX}otdb.task.feedback.processing

# -----------------------------------------
#   MACScheduler -> MessageRouter -> MoM
# -----------------------------------------

addtoQPIDDB.py --broker $MCU --queue ${PREFIX}lofar.task.specification.system --federation $CCU
addtoQPIDDB.py --broker $CCU --queue ${PREFIX}mom.task.specification.system --federation $MOM_SYSTEM

# -----------------------------------------
#   MoM <-> MoM-OTDB-Adapter
# -----------------------------------------

addtoQPIDDB.py --broker $CCU --queue mom.command --federation $MOM_SYSTEM
addtoQPIDDB.py --broker $CCU --queue mom.importxml --federation $MOM_SYSTEM
addtoQPIDDB.py --broker $MOM_SYSTEM --queue mom-otdb-adapter.importxml --federation $CCU

# -----------------------------------------
#   MoM Services
# -----------------------------------------
addtoQPIDDB.py --broker $MOM_SYSTEM --exchange ${PREFIX}lofar.mom.bus
addtoQPIDDB.py --broker $MOM_INGEST --exchange ${PREFIX}lofar.mom.bus
addtoQPIDDB.py --broker $MOM_SYSTEM --exchange ${PREFIX}lofar.mom.command
addtoQPIDDB.py --broker $MOM_SYSTEM --exchange ${PREFIX}lofar.mom.notification

# MoM queues that are unused functionally but still opened
addtoQPIDDB.py --broker $MOM_SYSTEM --queue ${PREFIX}mom.task.feedback.dataproducts
addtoQPIDDB.py --broker $MOM_SYSTEM --queue ${PREFIX}mom.task.feedback.processing

# -----------------------------------------
#   MoM Services <-> ResourceAssignment
# -----------------------------------------

addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.mom.bus --federation $MOM_SYSTEM
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.mom.command --federation $MOM_SYSTEM
addtoQPIDDB.py --broker $MOM_SYSTEM --exchange ${PREFIX}lofar.mom.notification --federation $SCU

# -----------------------------------------
#   Ingest
# -----------------------------------------

addtoQPIDDB.py --broker $LEXAR --exchange ${PREFIX}lofar.lta.ingest.command
addtoQPIDDB.py --broker $LEXAR --exchange ${PREFIX}lofar.lta.ingest.notification
addtoQPIDDB.py --broker $LEXAR --queue ${PREFIX}lofar.lta.ingest.jobs
addtoQPIDDB.py --broker $LEXAR --queue ${PREFIX}lofar.lta.ingest.jobs.for_transfer
addtoQPIDDB.py --broker $LEXAR --queue ${PREFIX}lofar.lta.ingest.notification.jobmanager
addtoQPIDDB.py --broker $LEXAR --bind --exchange ${PREFIX}lofar.lta.ingest.notification --queue ${PREFIX}lofar.lta.ingest.notification.momingestadapter --routingkey LTAIngest.#
addtoQPIDDB.py --broker $LEXAR --bind --exchange ${PREFIX}lofar.lta.ingest.notification --queue ${PREFIX}lofar.lta.ingest.notification.jobmanager --routingkey LTAIngest.#


# -----------------------------------------
#   ResourceAssignment
# -----------------------------------------
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.ra.command
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.ra.notification
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.otdb.command
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.otdb.notification
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.dm.command
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.dm.notification

# -----------------------------------------
#   QA
# -----------------------------------------

addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.qa.notification
addtoQPIDDB.py --broker $SCU --queue ${PREFIX}lofar.otdb.notification.for.qa_service


# -----------------------------------------
#   Specification & Trigger Services
# -----------------------------------------
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.spec.command
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.spec.notification
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.trigger.command
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.trigger.notification
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.mac.command
addtoQPIDDB.py --broker $SCU --exchange ${PREFIX}lofar.mac.notification

# -----------------------------------------
#   Specification -> MoM
# -----------------------------------------
addtoQPIDDB.py --broker $SCU --queue mom.importxml --federation $MOM_SYSTEM

# -----------------------------------------
#   Ingest -> SCU
# -----------------------------------------

addtoQPIDDB.py --broker $LEXAR --exchange ${PREFIX}lofar.lta.ingest.notification --federation $SCU

# -----------------------------------------
#   Ingest -> ResourceAssignment @ SCU
# -----------------------------------------

addtoQPIDDB.py --broker $SCU --queue ${PREFIX}lofar.lta.ingest.notification.autocleanupservice
addtoQPIDDB.py --broker $SCU --bind --exchange ${PREFIX}lofar.lta.ingest.notification --queue ${PREFIX}lofar.lta.ingest.notification.autocleanupservice --routingkey LTAIngest.#

# -----------------------------------------
#   Ingest -> LTA-storage-overview @ SCU
# -----------------------------------------

addtoQPIDDB.py --broker $LEXAR --queue ${PREFIX}lofar.lta.ingest.notification.for.ltastorageoverview
addtoQPIDDB.py --broker $LEXAR --bind --exchange ${PREFIX}lofar.lta.ingest.notification --queue ${PREFIX}lofar.lta.ingest.notification.for.ltastorageoverview --routingkey LTAIngest.#

