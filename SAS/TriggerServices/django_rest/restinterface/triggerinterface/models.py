"""
This is a stub. Currently not used, but can be implemented to get some better control on data in the interface,
do type checks, conversion, configure defaults, etc.
"""



from django.db import models
from django.utils import timezone

# Create your models here.

class Trigger(models.Model):

    pass # see note above

    # read-only:
    #submittedby= models.CharField(max_length=200,default='request.user', editable=False)
    #receivedat = models.DateTimeField(max_length=200,default=timezone.now, editable=False)
    # view_injected_get = models.CharField(max_length=200) # injection example

    # writable:
    #project_id = models.CharField(max_length=200)
    #metadata = models.CharField(max_length=20000, blank=True)
    #station_list = models.CharField(max_length=2000, blank=True)
    #qos = models.CharField(max_length=2000, blank=True )
    #spec = models.CharField(max_length=20000)
    #priority = models.IntegerField(max_length=200, default = 1000)
