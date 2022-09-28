# Welkin

Welkin is a Django app to connect to the Welkin Health API.

## Quick start

1. Add "django-welkin" to your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = [
    ...
    'django-welkin',
]
```

2. Include the django-welkin URLconf in your project urls.py like this:

    path('welkin/', include('django-welkin.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/welkin/configuration/
   to and add API secrets to the singleton (you'll need the Admin app enabled).
