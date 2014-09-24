import sys

sys.path.insert(0, 'openid.zip')

import django.core.handlers.wsgi

app = django.core.handlers.wsgi.WSGIHandler()
