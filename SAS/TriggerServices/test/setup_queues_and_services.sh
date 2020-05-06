#/bin/sh


source ~/dev/Triggers/Triggers-Taski10938/build/gnu_debug/lofarinit.sh

killall qpidd
killall specificationservice
killall specificationvalidationservice
killall specificationtranslationservice
killall triggerservice

echo "Setting up queues"
cd ~/dev/qpid-tools-0.32/src/py/
qpidd &
./qpid-config add exchange topic devel.lofar.spec.command
./qpid-config add exchange topic devel.lofar.trigger.command
./qpid-config add exchange topic devel.lofar.trigger.notification
./qpid-config add exchange topic devel.lofar.ra.command
./qpid-config add queue mom.importxml 



echo "Starting services"
specificationservice &
specificationvalidationservice & 
specificationtranslationservice & 
triggerservice & 
triggerrestinterface &

wait

