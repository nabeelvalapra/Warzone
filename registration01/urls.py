from django.conf.urls import patterns, include, url
from registration01 import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Warzone.views.home', name='home'),
    
    #url(r'^login/', views.login , name='login'),
    url(r'^$', views.login , name='login'),
    url(r'^authenticate/', views.auth_login , name='auth_login'),
    url(r'^loggedin/', views.loggedin , name='login'),
    url(r'^register/', views.register ,name='register'),
    url(r'^registration_success/', views.registration_success ,name='registration_success'),
    
)