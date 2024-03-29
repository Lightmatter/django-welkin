# Welkin

Welkin is a Django app to connect to the Welkin Health API.

## Quick start

1. Install django-welkin with pip:

```
pip install django-welkin
```

2. Add django-welkin and django-solo to your INSTALLED_APPS setting like this:

```python
INSTALLED_APPS = [
    ...
    "solo",
    'django_welkin',
]
```

3. Include the django-welkin URLconf in your project urls.py like this:

```python
path('welkin/', include('django_welkin.urls')),
```

4. Run `python manage.py migrate` to create the welkin models.

5. Start the development server and visit http://localhost:8000/admin/welkin/configuration/
   to and add API secrets to the singleton (you'll need the Admin app enabled).

## Configuration

### Syncing Users
The sync command will only sync the users who have one of the roles in `settings.WELKIN_SYNC_ROLES`.
When set this should be a list containing the roles that are allowed to be synced.
For instance by default this list is:
```py
["health-coach", "physician"]
```
