from django.conf.urls import patterns, url
from gdrive import views



urlpatterns = patterns('',
         
         url(r'^firstwar/$', views.firstwar ,name='mainpage'),
        
        url(r'^secondwar/$' , views.upload2 , name='mainpage2'),
        #url(r'^secondwar/(?P<code>\w+)/$' , views.gdrive_callback , name='callback'),
        url(r'secondwar/logout/$', views.logoutfromhere , name='logout')

)