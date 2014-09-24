from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^$', views.mainpage),
    url(r'^openid/', include('gae-openid.urls'), {'success_handler': views.success_handler}),
)
