from django.conf.urls.defaults import patterns
import views

urlpatterns = patterns('',
  (r'^start/$', views.OpenIDStartSubmit, name='openid_start'),
  (r'^finish/$', views.OpenIDFinish, name='openid_finish'),
  (r'^rpxrds/$', views.RelyingPartyXRDS),
  (r'^error/(?P<err_id>.*)/$', views.ErrorPage),
)
