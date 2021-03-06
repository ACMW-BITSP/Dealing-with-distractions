"""dwd URL Configuration

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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

from .settings import common

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='homepage.html'),
        name='homepage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^mcqs/', include('mcqs.urls', namespace='mcqs')),
    url(r'^coding/', include('coding.urls', namespace='coding')),
    url(r'^team/', include('teams.urls', namespace='teams')),
    url(r'^scores/', include('scores.urls', namespace='scores')),
] + static(common.STATIC_URL, document_root=common.STATIC_ROOT)


