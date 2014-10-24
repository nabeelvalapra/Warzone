from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Warzone.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^hello/',include('hello.urls')),
   
    url(r'^registration01/',include('registration01.urls')),
    url(r'^registration02/',include('registration02.urls')),

    url(r'^gdrive/',include('gdrive.urls')),
    
    url(r'^fmzone/',include('fmzone.urls')),
    
    
)
