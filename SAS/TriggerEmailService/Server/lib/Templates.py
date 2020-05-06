RECEIVED_TEMPLATE_SUBJECT = """%(PROJECTNAME)s trigger %(TRIGGERID)s received"""
ACCEPTED_TEMPLATE_SUBJECT = """%(PROJECTNAME)s trigger %(TRIGGERID)s scheduled"""
REJECTED_TEMPLATE_SUBJECT = """%(PROJECTNAME)s trigger %(TRIGGERID)s cancelled"""
ABORTED_TEMPLATE_SUBJECT = """%(PROJECTNAME)s trigger %(TRIGGERID)s aborted"""
FINISHED_TEMPLATE_SUBJECT = """%(PROJECTNAME)s trigger %(TRIGGERID)s completed"""

RECEIVED_TEMPLATE_BODY = """Dear PI/Project Contact,

We have received a trigger for your project %(PROJECTNAME)s with ID %(TRIGGERID)s. Please find the received trigger file attached.

The requested time to schedule the trigger is between %(STARTTIME)s UTC and %(ENDTIME)s UTC. The system will now determine if your trigger can be scheduled within the restrictions specified in the trigger.

kind regards,

LOFAR Science Operations & Support [ sos@astron.nl ]"""
ACCEPTED_TEMPLATE_BODY = """Dear PI/Project Contact,

This is a follow up message for the trigger for your project %(PROJECTNAME)s with ID %(TRIGGERID)s.

The trigger has been scheduled.

The observation IDs are %(OBSSASID)s, the MoM IDs are %(OBSMOMID)s.

To follow the progress and check the details, please check the observation in MoM %(MOMLINK)s.

kind regards,

LOFAR Science Operations & Support [ sos@astron.nl ]"""
REJECTED_TEMPLATE_BODY = """Dear PI/Project Contact,

This is a follow up message for the trigger for your project %(PROJECTNAME)s with ID %(TRIGGERID)s.

We are sorry to inform you that your trigger could not be scheduled at this time. This is either because no resources are available at the requested time and duration, or because you have used up all your triggers. This trigger will not count towards your quota.

kind regards,

LOFAR Science Operations & Support [ sos@astron.nl ]"""
ABORTED_TEMPLATE_BODY = """Dear PI/Project Contact,

This is a follow up message for the trigger for your project %(PROJECTNAME)s with ID %(TRIGGERID)s.

We are sorry to inform you that the scheduled observation has aborted.

The observation IDs are %(OBSSASID)s, the MoM ID is %(OBSMOMID)s.

Science Support and Operations will be in contact with you about the further process and to see if any of the data can still be used. You can find the observation in MoM %(MOMLINK)s.

kind regards,

LOFAR Science Operations & Support [ sos@astron.nl ]"""
FINISHED_TEMPLATE_BODY = """Dear PI/Project Contact,

This is a follow up message for the trigger for your project %(PROJECTNAME)s with ID %(TRIGGERID)s.

The triggered observations have completed.

The observation IDs are %(OBSSASID)s, the MoM ID is %(OBSMOMID)s.

To follow the progress and check the details, please check the observation in MoM %(MOMLINK)s.

Science Operations and Support will contact you about the further process in processing and ingesting the data.

kind regards,

LOFAR Science Operations & Support [ sos@astron.nl ]"""
