from django.conf.urls import patterns, url
from gdrive import views



urlpatterns = patterns('',
         
         url(r'^firstwar/$', views.firstwar ,name='mainpage'),
        
        url(r'^secondwar/$' , views.upload2 , name='mainpage2'),

)