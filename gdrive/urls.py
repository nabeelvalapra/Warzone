from django.conf.urls import patterns, url
from gdrive import views, GoogleDriveFunctions



urlpatterns = patterns('',
         
        url(r'^firstwar/$', views.firstwar ,name='mainpage'),
        url(r'^secondwar/$', views.index2, name='index2'),
        url(r'^secondwar/upload2/$' , views.upload2 , kwargs={'credentials':''}, name='mainpage2'),
        url(r'^secondwar/listGfiles/$' , views.listGfiles , name='listGfiles'),
        url(r'^secondwar/handlelist/$' , views.handlelist , name='handlelist'),
        #url(r'^secondwar/auth/$', views.login_GoogleDrive, name='login_GoogleDrive'),
        url(r'^secondwar/code/$' , GoogleDriveFunctions.gdrive_callback , name='callback'),
        url(r'secondwar/logout/$', views.logoutfromhere , name='logout')

)