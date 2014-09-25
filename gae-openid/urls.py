from django.conf.urls.defaults import *

import sys, os
opeid_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openid.zip')
if opeid_lib not in sys.path:
  sys.path.insert(0, opeid_lib)

import views

urlpatterns = patterns('',
  url(r'^start/$', views.OpenIDStartSubmit, name='openid_start'),
  url(r'^finish/$', views.OpenIDFinish, name='openid_finish'),
  url(r'^rpxrds/$', views.RelyingPartyXRDS),
  url(r'^error/(?P<err_id>.*)/$', views.ErrorPage),
)
