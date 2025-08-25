from django.urls import path
from . import views

urlpatterns = [
    # Router management
    path('', views.router_list, name='router-list'),
    path('<int:pk>/', views.router_detail, name='router-detail'),
    path('<int:pk>/test-connection/', views.test_connection, name='test-connection'),
    path('<int:pk>/execute-command/', views.execute_command, name='execute-command'),
    path('<int:pk>/device-info/', views.get_device_info, name='get-device-info'),
    path('<int:pk>/packages/', views.get_router_packages, name='get-router-packages'),
    
    # Package management
    path('packages/', views.package_list, name='package-list'),
    path('packages/<int:pk>/', views.package_detail, name='package-detail'),
]
