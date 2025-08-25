"""
URL configuration for mikrotik_cloudpilot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer


schema_title = "Mikrotik CloudPilot API"
schema_description = "OpenAPI schema for Mikrotik CloudPilot API"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('routers/', include('routers.urls')),
    path('payments/', include('payments.urls')),
    # OpenAPI schema endpoint (JSON)
    path(
        'openapi.json',
        get_schema_view(
            title=schema_title,
            description=schema_description,
            version='1.0.0',
            public=True,
            renderer_classes=[JSONOpenAPIRenderer],
        ),
        name='openapi-json',
    ),
]
