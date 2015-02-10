from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/', include('msgvis.apps.api.urls')),
                       url(r'^docs/', include('docs.urls')),
                       url(r'^', include('msgvis.apps.base.urls')),
)
