from django.conf.urls import patterns, url
from gdrive import views



urlpatterns = patterns('',
         
        url(r'^$', views.letitgo ,name='mainpage'),
        
)