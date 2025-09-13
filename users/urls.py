from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('api-key-login/', views.api_key_login, name='api-key-login'),
    path('profile/', views.user_profile, name='user-profile'),
    path('api-keys/', views.get_api_keys, name='get-api-keys'),
    path('generate-api-key/', views.generate_api_key, name='generate-api-key'),
    path('rotate-api-keys/', views.rotate_api_keys, name='rotate-api-keys'),
    path('set-custom-api-keys/', views.set_custom_api_keys, name='set-custom-api-keys'),
]
