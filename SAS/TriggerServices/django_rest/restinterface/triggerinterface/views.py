"""
Handles GET / POST requests by users.
"""

import os

from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
#from serializers import TriggerSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from io import BytesIO
from rest_framework.fields import CurrentUserDefault
from lxml import etree
from io import BytesIO

from lofar.triggerservices.trigger_service_rpc import TriggerRPC
from lofar.specificationservices.specification_service_rpc import SpecificationRPC
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lofar.messaging import ToBus, EventMessage, RPCException, DEFAULT_BROKER, DEFAULT_BUSNAME

import logging
import traceback
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

triggerrpc = TriggerRPC()
specrpc = SpecificationRPC()
momrpc = MoMQueryRPC()

from .config import TRIGGER_SUBMISSION_NOTIFICATION_SUBJECT
notification_bus = ToBus()

# The base URL for triggers specifications
base_url = 'https://lofar.astron.nl/mom3/user/main/explorer/setUpExplorer.do?action=open&object=FP1_CF'
if "LOFARENV" in os.environ:
    lofar_environment = os.environ['LOFARENV']

    if lofar_environment != "PRODUCTION":
        base_url = 'http://lofartest.control.lofar:8080/mom3/user/main/explorer/setUpExplorer.do?action=open&object=FP1_CF'


class TriggerListView(views.APIView):

    def __init__(self, **kwargs):
        super(TriggerListView, self).__init__(**kwargs)
        notification_bus.open()

    def get(self, request, format=None, **kwargs):
        logger.debug('got GET from -> ' + str(request.META['REMOTE_ADDR']))
        with momrpc:
            result = momrpc.get_triggers(str(request.user))['triggers']

        # Add the MoM URL for the project.
        # result = {'mom_id': mom_id,
        #       'project_name': projectName,
        #       'arrival_time': arrival_time,
        #       'status': status,
        #       'momurl_id': momurl_id}
        # -> new_result['mom_id']['url'] = url for the project containing the trigger
        # -> new_result['mom_id']['status'] = status of the project
        # -> new_result['mom_id']['trigger_info'][trigger_id] = {arrival time, project name}
        mom_ids = {}
        for trigger_id, trigger_details in result.items():
            project_name = trigger_details['project_name']
            mom_id = trigger_details['mom_id']
            arrival_time = trigger_details['arrival_time']
            status = trigger_details['status']

            # Initialise the dict at [mom_id][]
            if mom_id not in mom_ids:
                mom_ids[mom_id] = {}
                mom_ids[mom_id]['trigger_info'] = {}
                # Fill the mom_id entry with info relevant to all
                # triggers of that mom id.
                momurl_id = trigger_details['momurl_id']
                url = base_url + momurl_id
                mom_ids[mom_id]['url'] = url
                mom_ids[mom_id]['status'] = status

            mom_ids[mom_id]['trigger_info'][trigger_id] = {
                'project_name': project_name,
                'arrival_time': arrival_time}

        # If the requested format is not HTML return the triggers unmodified.
        if 'format' not in request.GET or request.GET['format'] != 'html':
            return Response(mom_ids)

        # The HTML representation of the triggers gets a bit beautified.
        htmlContent = '<h2 align=center>LOFAR triggers for user ' + str(request.user) + '</h2>'

        for mom_id, mom_details in mom_ids.items():
            htmlContent += '<p><table border=1 align=center>' + \
                '<tr><th colspan=3>MoM id: ' + mom_id + '</th></tr>' + \
                '<tr><th colspan=3>Status: ' + mom_details['status'] + '</th></tr>' + \
                '<tr><th colspan=3>URL: <a href=' + mom_details['url'] + ' target=_blank>' + mom_details['url'] + '</a></th></tr>' + \
                '<tr><th>Trigger ID</th><th>Project Name</th><th>Arrival Time</th>'
            for trigger_id, trigger_details in mom_details['trigger_info'].items():
                htmlContent += '<tr><td align=center><a href=/triggers/' + trigger_id + '/?format=xml target=_blank>' + trigger_id + '</a></td>' + \
                '<td align=center>' + trigger_details['project_name'] + '</td>' + \
                '<td align=center>' + trigger_details['arrival_time'] + '</td>' + \
                '</tr>'
            htmlContent += '</table></p>'

        return Response(htmlContent)

    def post(self, request, format=None, **kwargs):
        IP = str(request.META['REMOTE_ADDR'])
        logger.debug('got POST from -> '+IP)
        #logger.debug('received text -> '+str(request.body))
        #logger.debug('received data -> '+str(request.data))
        logger.debug('from user -> '+str( request.user))
        self._sendNotification(str(request.user), IP)


        # OPTIONALLY USE DATA MODEL:
        #serializer = TriggerSerializer(data=request.data)
        #logger.debug('data is valid -> ' +str(serializer.is_valid()))
        #if serializer.is_valid():
        #    id = serializer.save(request.user)
        #    #r = serializer.validated_data
        #    #r["trigger_id"]=id

        # EITHER: RENDER FRESH XML FROM PARSED DATA:
        #xml = XMLRenderer().render(request.data) # ! django replaces the root element
        #xml = self._renameXMLroot(xml, "lofar:trigger")
        #print xml

        # OR: USE RECEIVED XML DIRECTLY:
        xml = request.body.decode('utf8')

        logger.debug('calling trigger handler')
        try:
            response = self._handle_trigger(str(request.user), IP, xml)
            identifier = response.get('trigger-id')
        except RPCException as err:
            #traceback.print_exc()
            issues = str(err) # remove internal details. For some reason the error message also contains the backtrace. Introduced by RPC?
            return Response('Provided data has some issues! (Details: '+issues+")",  status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            #traceback.print_exc()
            issues = str(str(err).split('File')[0]) # remove internal details. For some reason the error message also contains the backtrace. Introduced by RPC?
            return Response('Provided data has some issues! (Details: '+issues+")",  status=status.HTTP_400_BAD_REQUEST)
            # for use with data model:  return Response('Provided data has some issues: ' +str(serializer.errors)+" (Accepted were: "+str(serializer.data)+")", status=status.HTTP_400_BAD_REQUEST)

        return Response(identifier, status=status.HTTP_201_CREATED)

    def _renameXMLroot(self, xml, newname):
        root = etree.parse(BytesIO(xml))
        root.tag = newname
        return etree.tostring(root)

    def _handle_trigger(self, user, host, xml):
        with triggerrpc:
            return triggerrpc.handle_trigger(user, host, xml)

    def _sendNotification(self, user, IP):
        msg = EventMessage(subject=TRIGGER_SUBMISSION_NOTIFICATION_SUBJECT, content="Trigger received by "+str(user)+" (IP:"+IP+")")
        try:
            notification_bus.send(msg)
        except Exception as err:
            logger.error("Could not send notification ->" + str(err))




class TriggerView(views.APIView):


    #def post(self, request, format=None, **kwargs):
    #    return Response("It is not possible to alter an existing trigger (i.e. POST for an existing trigger ID), sorry!", status=status.HTTP_405_METHOD_NOT_ALLOWED)


    def get(self,request, format=None, **kwargs):
        logger.debug('got GET from: '+str(request.META['REMOTE_ADDR']))
        try:
            if 'pk' in kwargs:
                identifier = kwargs.get('pk')
                logger.info('requested id is: '+str(identifier))
                logger.info('requesting user is:'+ str(request.user))

                xml = self._get_specification(str(request.user), str(identifier))['trigger_spec']

                # EITHER DIRECT RESPONSE:
                return Response(xml)

                # OR USE DATA MODEL:
                # data = XMLParser().parse(BytesIO(xml))

                # example: data injection with validation:
                # data['view_injected_get'] = 'pre-serializing'

                #serializer = TriggerSerializer(data=data)
                #logger.debug('returning valid data:' + str(serializer.is_valid()))
                #r = serializer.validated_data

                # example: data injection after validation:
                # r['view_injected_get_2'] = 'post-validation'

                #return Response(r)
            else:
                return Response("No ID provided!")
        except Exception as err:
            print(err)
            return Response("Unable to retrieve the requested trigger, sorry!", status=status.HTTP_404_NOT_FOUND)


    def _get_specification(self, user, identifier):

        logger.info("Getting spec from specification service")

        with specrpc:
            response = specrpc.get_specification(user, identifier)
        return response

        # test json data:
        #json = '{"project_id": "p1", "triggerid": "t1", "triggerxml": "<trigger />", "status": "new", "momid": "m1", "sasid": "s1", "submittedby":"user"}'
        #stream = BytesIO(json)
        #data = JSONParser().parse(stream)
        # return XMLRenderer().render(data)


