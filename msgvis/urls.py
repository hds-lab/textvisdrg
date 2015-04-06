from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api/', include('msgvis.apps.api.urls')),
                       url(r'^docs/', include('docs.urls')),
                       url(r'^', include('msgvis.apps.base.urls')),
                       url(r'^topics/', include('msgvis.apps.enhance.urls')),
)

from django.conf import settings
if 'debug_toolbar' in settings.INSTALLED_APPS and not settings.DEBUG_TOOLBAR_PATCH_SETTINGS:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
