"""wikidata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from django.views.generic.base import TemplateView


from report import views

router = DefaultRouter()
router.register(r'taskrun', views.TaskRunViewSet)
router.register(r'logs', views.LogViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'items', views.ItemViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^barchart/$', TemplateView.as_view(template_name='barchart.html'), name="chart"),
    url(r'^chart/$', TemplateView.as_view(template_name='chart.html'), name="chart"),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^uploadPOST/$', views.uploadPOST, name='uploadPOST'),
]