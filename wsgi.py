import sys
import os

import django.core.handlers.wsgi

opeid_lib = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'gae-openid',
    'openid.zip'
)

if opeid_lib not in sys.path:
    sys.path.insert(0, opeid_lib)


app = django.core.handlers.wsgi.WSGIHandler()
