from django.conf.urls import patterns, include, url
from hello import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Warzone.views.home', name='home'),
    
    url(r'^$', views.startpage , name='startpage'),
)