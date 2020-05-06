from lofar.messaging import adaptNameToEnvironment


DEFAULT_INGEST_PREFIX = 'LTA.Ingest'
INGEST_NOTIFICATION_PREFIX = DEFAULT_INGEST_PREFIX + ".notification"
DEFAULT_INGEST_SERVICENAME = DEFAULT_INGEST_PREFIX + ".service"

def hostnameToIp(hostname):
    if 'lexar003' in hostname:
        return '10.178.1.3'
    if 'lexar004' in hostname:
        return '10.178.1.4'

    import socket
    return socket.gethostbyname(hostname)
