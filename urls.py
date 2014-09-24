from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
  url(r'^$', views.mainpage),
  url(r'^_ah/warmup$', views.mainpage),
  url(r'^openid/', include('gae-openid.urls')),
)
