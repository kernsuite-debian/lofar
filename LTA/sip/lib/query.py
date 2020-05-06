# This module allows querying MoM / the catalog for SIPs of related dataproducts that can be added with the full history to a new SIP.
# This is preliminary, for use by the pilot user. Should be cleaned up / replaced by some alternative method

import urllib.request, urllib.parse, urllib.error
import requests
from os.path import expanduser, exists
import xml.etree.ElementTree as ET
import xmlrpc.client
import uuid
import copy

path = expanduser("~/.siplibrc")
user = None
passw = None
#host = "lta-ingest-test.lofar.eu:19443"
host = "lofar-ingest.target.rug.nl:9443"

if not exists(path):
    # write default file
    with open(path, 'w') as file:
        file.write("user=\n")
        file.write("password=\n")
        file.write("host=\n")

with open(path,'r') as file:
        print("Parsing user credentials from",path)
        for line in file:
            if line.startswith("user"):
                user = line.split('=')[1].strip()
            if line.startswith("password"):
                passw = line.split('=')[1].strip()
            if line.startswith("host"):
                host = line.split('=')[1].strip()

login_data = {
    'j_username' : user,
    'j_password' : passw
    }

url = 'https://'+user+':'+passw+'@'+host
client = xmlrpc.client.ServerProxy(url)

# id_cache = {}

def _call_idservice(source, userlabel=None):

    if userlabel is not None:
        response = client.GetUniqueIDForLabel(source, userlabel)
    else:
        response = client.GetUniqueID(source)
    return response

# for testing:
    # if userlabel in id_cache:
    #     print "using existing", userlabel
    #     response = id_cache.get(userlabel)
    # else:
    #     print "creating new", userlabel
    #     response = {"version": "version",
    #                 "result": "ok",
    #                 "id": uuid.uuid1().int>>64,
    #                 "user_label": userlabel,
    #                 "data_type": "type",
    #                 "identifier_source": source,
    #                 "is_new": True,
    #                 "error": ''}
    #     if userlabel is not None:
    #         print "keeping copy", userlabel
    #         keeper = copy.deepcopy(response)
    #         keeper["is_new"] = False
    #         id_cache[userlabel] = keeper
    #
    # return response


def create_unique_id(source, userlabel=None):
    """
    Creates a new unique numeric identifier in the LTA catalog for the given source name.
    An optional userlabel can be assigned to later query the identifier based on this String.
    Throws an exception if the given label already exists for the given source.
    """
    response = _call_idservice(source, userlabel)
    if not response.get("result") == "ok":
        raise Exception('An identifier for this userlabel could not be created -> '+str(response.get("error")))
    if not response.get("is_new"):
        raise Exception('An identifier for this userlabel already exists -> '+str(userlabel))
    return response.get('id')


def get_unique_id(source, userlabel):
    """
    Queries an existing numeric ID from the LTA catalog based on it's userlabel (which had
    to be assigned at the time the Identifier is created to allow this lookup to work).
    Throws an exception if the given label does not exist for the given source.
    """
    response = _call_idservice(source, userlabel)
    if not response.get("result") == "ok":
        raise Exception('An identifier for this userlabel could not be retrieved -> '+str(response.get("error")))
    if response.get("is_new"):
        raise Exception('An identifier for this userlabel does not exist -> '+str(userlabel))
    return response.get('id')



def get_dataproduct_sip(projectname,dataproductid):
    return client.GetSip(projectname,dataproductid).get("sip")

def get_dataproduct_ids(projectname, sasid):
    return client.GetDataProductIDS(projectname,sasid).get("ids")
