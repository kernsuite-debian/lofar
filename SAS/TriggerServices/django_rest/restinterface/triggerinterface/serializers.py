"""
This is a stub.
Currently not used, but can be implemented to populate and validate the trigger data model.
Check views.py for data parsing and rendering on get/post.
"""


from rest_framework import serializers
from .models import Trigger
from rest_framework_xml.renderers import XMLRenderer
from django.utils import timezone

import trigger_handler
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TriggerSerializer(serializers.ModelSerializer):

    #submittedby= serializers.CharField(max_length=200, read_only=True)
    #receivedat = serializers.DateTimeField(default=timezone.now)

    def save(self, user):
        logger.debug('saving data')
        logger.debug('data ->' + str(self.data))
        logger.debug('validated data ->' + str(self.validated_data))
        logger.debug('fields ->' + str(self.fields))
        logger.debug('errors ->' + str(self.errors))
        logger.debug('rendering XML')
        xml = XMLRenderer().render(self.validated_data)
        logger.debug('calling trigger handler')
        id = trigger_handler.handle_trigger(user, xml)
        return id

    class Meta:
        model = Trigger
        fields = '__all__'

