

------------------------------
Trigger rest interface README.
------------------------------

This web service will build as part of the package Trigger_Services.
The executable 'triggerrestinterface' or running 'manage.py runserver' will start a local service (-> http://localhost:8000/triggers/).

The interface is not making use of a local database, but the django rest framework requires one, and so the service
will create a local sqlite database file if none is present.

Run 'manage.py migrate' to remove warnings abot missing migrations.
Run 'manage.py collectstatic' to collect static files for deployment in Apache