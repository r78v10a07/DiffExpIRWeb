"""rvera URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url

from project.main import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^prj/(?P<id>\d*)/$', views.project, name="prj"),
    url(r'^prj/$', views.project, name="prj"),
    url(r'^exp/(?P<id>\d*)/$', views.experiment, name="exp"),
    url(r'^intron/(?P<id>\d*)/$', views.intron, name="intron"),
    url(r'^service/$', views.service, name="service"),
]
