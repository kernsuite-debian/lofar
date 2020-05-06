#!/usr/bin/env python3

from lofar.qpidinfrastructure.QPIDDB import qpidinfra
from lofar.common import dbcredentials

def qpidconfig_add_queue(settings):
    print(("qpid-config -b %s add queue %s --durable" %(settings['hostname'],settings['queuename'])))

def qpidconfig_add_topic(settings):
    print(("qpid-config -b %s add exchange topic %s --durable" %(settings['hostname'],settings['exchangename'])))

def qpidroute_add(settings):
    cmd = "dynamic" if settings['dynamic'] else "route"

    print(("qpid-route -d route del %s %s %s \'%s\' " %(settings['tohost'],settings['fromhost'],settings['exchangename'],settings['routingkey'])))
    print(("qpid-route -d dynamic del %s %s %s" %(settings['tohost'],settings['fromhost'],settings['exchangename'])))

    if settings['dynamic']:
        print(("qpid-route -d dynamic add %s %s %s" %(settings['tohost'],settings['fromhost'],settings['exchangename'])))
    else:
        print(("qpid-route -d route add %s %s %s \'%s\' " %(settings['tohost'],settings['fromhost'],settings['exchangename'],settings['routingkey'])))

def qpidQroute_add(settings):
    print(("qpid-route -d queue del %s %s '%s' '%s'" %(settings['tohost'],settings['fromhost'],settings['exchangename'],settings['queuename'])))
    print(("qpid-route -d queue add %s %s '%s' '%s'" %(settings['tohost'],settings['fromhost'],settings['exchangename'],settings['queuename'])))

def qpidconfig_add_binding(settings):
    print(("qpid-config --durable -b %s bind %s %s %s" %(settings['hostname'],settings['exchangename'],settings['queuename'],settings['routingkey'])))

dbcreds = dbcredentials.DBCredentials().get("qpidinfra")
QPIDinfra = qpidinfra(dbcreds)
QPIDinfra.perqueue(qpidconfig_add_queue)
QPIDinfra.perexchange(qpidconfig_add_topic)
QPIDinfra.perfederationexchange(qpidroute_add)
QPIDinfra.perfederationqueue(qpidQroute_add)
QPIDinfra.perqpidbinding(qpidconfig_add_binding)

