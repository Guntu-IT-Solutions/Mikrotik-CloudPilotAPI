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
from django.conf import settings
from django.conf.urls.static import static
from .views import serve_docs, docs_home


schema_title = "Mikrotik CloudPilot API"
schema_description = "OpenAPI schema for Mikrotik CloudPilot API"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('routers/', include('routers.urls')),
    path('payments/', include('payments.urls')),
    # Documentation routes
    path('docs/', docs_home, name='docs_home'),
    path('docs/<path:path>', serve_docs, name='serve_docs'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
