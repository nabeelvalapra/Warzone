from django.conf.urls import patterns, include, url
from makenotification import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Warzone.views.home', name='home'),
    
    url(r'^$', views.index , name='index'),
    url(r'^gonotify$', views.gonotify , name='gonotify'),

)