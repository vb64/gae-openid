from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
  url(r'^start/$', views.OpenIDStartSubmit, {}, name='openid_start'),
  url(r'^finish/$', views.OpenIDFinish, name='openid_finish'),
  url(r'^rpxrds/$', views.RelyingPartyXRDS, {}),
  url(r'^error/(?P<err_id>.*)/$', views.ErrorPage, {}),
)
