"""
WSGI config for triggerservice project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lofar.triggerservices.restinterface.settings")

_application = get_wsgi_application()

def application(environ, start_response):
  # LOFARENV can be set (e.g. using SetEnv in Apache)
  if 'LOFARENV' in environ:
    os.environ['LOFARENV'] = environ['LOFARENV']
  return _application(environ, start_response)

