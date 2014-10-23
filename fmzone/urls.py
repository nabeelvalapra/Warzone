from django.conf.urls import patterns, include, url
from fmzone import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Warzone.views.home', name='home'),
    
    url(r'^$', views.details , name='details'),
    url(r'^formset/', views.outforms , name='outform')
)