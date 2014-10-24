from django.conf.urls import patterns, url
from gdrive import views



urlpatterns = patterns('',
         
        url(r'^firstwar/$', views.upload ,name='mainpage'),
        url(r'^callback/$', views.gdrive_callback , name='gdrive_callback'),
)