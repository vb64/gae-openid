GAE-OpenID
==========

[Live version](http://openid-gae.appspot.com) of this code.

Django library for authorization with Wargaming OpenID on Google App Engine platform.

based on: 
[demand.openid.net](https://code.google.com/p/demand/) included as zip archive.
[google-app-engine-django-openid](https://code.google.com/p/google-app-engine-django-openid/)

Main difference from google-app-engine-django-openid is a using GAE memcache for saving openid session data, instead GAE datastore tables. So don't need db tables for this purpose, and their periodically cleanup.

**Usage in your Django App**

**1.** Define handler for success OpenID auth as:

```
def success_handler(request, response, openid_url)
```

where request, response are the standard django objects, and openid_url is a auth data from wargaming.

**2.** Include library urls handlers and your function from step 1 into your url.py. 

For example:

```
urlpatterns = patterns('',
    ...
    url(r'^openid/', include('gae-openid.urls'), {'success_handler': module.success_handler}),
    ...
)
```

**3.** Add library middleware module into your settings.py:

```
MIDDLEWARE_CLASSES = (
    ...
    'gae-openid.middleware.OpenIDMiddleware',
    ...
)
```

Into templates, for entry point to wargaming OpenID auth, you can use, for example:

```
{% url openid_start %}?continue=/&openid_identifier=https://ru.wargaming.net/id/
```
