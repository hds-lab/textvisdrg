from django.conf.urls import patterns, include, url
from django.contrib import admin

from msgvis.apps.base import views

urlpatterns = patterns('',
                       url(r'^$', views.HomeView.as_view(), name='home'),
                       # url(r'^explorer/$', views.ExplorerView.as_view(), name='explorer'),
                       url(r'^explorer(?:/(?P<dataset_pk>\d+))?/$', views.ExplorerView.as_view(), name='explorer'),
                       url(r'^grouper(?:/(?P<dataset_pk>\d+))?/$', views.GrouperView.as_view(), name='grouper'),
)
