.. toctree::
   :hidden:

   self

#########
django-welkin
#########
**A Django app for interfacing with the Welkin Health API.**

|Version| |License|

.. |Version| image:: https://img.shields.io/pypi/v/django-welkin
   :target: https://pypi.org/project/django-welkin/

.. |License| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0

This package allows Python developers to write software that makes use of the Welkin Health API. Functions available in the API are mirrored in this package as closely as possible, translating JSON responses to Python objects. You can find the current documentation for the Welkin Health API here:

`Welkin Health API Documentation <https://developers.welkinhealth.com/>`_

**********
Installation
**********
Install with pip:
.. code-block::

   pip install welkin

Or with Poetry:
.. code-block::

   poetry add welkin

**********
Configuration
**********
Add django-welkin and django-solo to your INSTALLED_APPS:

.. code-block::

   INSTALLED_APPS = [
      ...
      "solo",
      "django_welkin",
   ]

Include the django-welkin URLS in your project urls.py:
.. code-block::

   path('welkin/', include('django_welkin.urls'), namespace="welkin"),

Apply the django-welkin migrations:

.. code-block::

   python manage.py migrate

Start the development server and visit http://localhost:8000/admin/welkin/apikey/
to and add API secrets for your Welkin instance (you'll need the Admin app enabled).

Sync your database with Welkin:

.. code-block::

   python manage.py welkin_sync_models
