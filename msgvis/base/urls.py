from django.conf.urls import patterns, include, url
from django.contrib import admin

from msgvis.base.views import home

urlpatterns = patterns('',
                       url(r'^$', home, name='home'),
)
