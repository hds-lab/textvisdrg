from django.conf.urls import patterns, include, url
from django.contrib import admin

from msgvis.base import views

urlpatterns = patterns('',
                       url(r'^$', views.HomeView.as_view(), name='home'),
                       url(r'^explorer/$', views.ExplorerView.as_view(), name='explorer'),
)
