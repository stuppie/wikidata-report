from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from django.views.generic.base import TemplateView


from . import views

urlpatterns = [
    url(r'^errors$', views.index, name='index'),
]