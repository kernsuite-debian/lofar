import os
import logging
logger = logging.getLogger()

import kombu
# make default kombu/amqp logger less spammy
logging.getLogger("amqp").setLevel(logging.INFO)

from lofar.messaging import adaptNameToEnvironment
from lofar.common import isProductionEnvironment, isTestEnvironment

# the DEFAULT_BROKER that's used in lofar's messaging refers to the single
# broker at either the production or test scu, depending on the runtime environment.
# For a non-production/non-test env, just use localhost.
DEFAULT_BROKER = "scu001.control.lofar" if isProductionEnvironment() else \
                 "scu199.control.lofar" if isTestEnvironment() else \
                 "localhost"

if 'LOFAR_DEFAULT_BROKER' in os.environ.keys():
    DEFAULT_BROKER = os.environ.get('LOFAR_DEFAULT_BROKER')

DEFAULT_USER = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
DEFAULT_PASSWORD = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')

if isProductionEnvironment() or isTestEnvironment():
    # import the user and password from RabbitMQ 'db'credentials
    try:
        from lofar.common.dbcredentials import DBCredentials
        _db_creds = DBCredentials().get("RabbitMQ")
        DEFAULT_USER = _db_creds.user
        DEFAULT_PASSWORD = _db_creds.password
    except:
        pass


# dynamically determine port where RabbitMQ server runs by trying to connect
DEFAULT_PORT = -1

def broker_url(hostname: str=DEFAULT_BROKER, port: int=DEFAULT_PORT, userid: str=DEFAULT_USER, password :str=DEFAULT_PASSWORD) -> str:
    return 'amqp://%s:%s@%s:%d//' % (userid, password, hostname, port)

for port in [5672, 5675]:
    try:
        logger.debug("trying to connect to broker: hostname=%s port=%s userid=%s password=***",
                     DEFAULT_BROKER, port, DEFAULT_USER)
        with kombu.Connection(broker_url(port=port), max_retries=0, connect_timeout=1, ) as connection:
            connection.connect()
            DEFAULT_PORT = port
            logger.info("detected rabbitmq broker to which we can connect with hostname=%s port=%s userid=%s password=***",
                        DEFAULT_BROKER, port, DEFAULT_USER)
            break
    except Exception as e:
        logger.debug("cannot connect to broker: hostname=%s port=%s userid=%s password=*** error=%s",
                     DEFAULT_BROKER, port, DEFAULT_USER, e)

# default exchange to use for publishing messages
DEFAULT_BUSNAME = adaptNameToEnvironment("lofar")

