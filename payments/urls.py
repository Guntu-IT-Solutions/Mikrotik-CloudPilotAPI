from django.urls import path
from . import views

urlpatterns = [
    # Payment Credentials URLs
    path('credentials/', views.payment_credentials_list, name='payment_credentials_list'),
    path('credentials/<int:pk>/', views.payment_credentials_detail, name='payment_credentials_detail'),
    path('credentials/<int:pk>/update-private-key/', views.update_private_key, name='update_private_key'),
    path('credentials/<int:pk>/verify/', views.verify_credentials, name='verify_credentials'),
    path('credentials/<int:pk>/get-private-key/', views.get_private_key, name='get_private_key'),
    path('credentials/provider/<str:provider>/', views.payment_credentials_by_provider, name='payment_credentials_by_provider'),
    path('credentials/<int:pk>/toggle/', views.toggle_credentials_status, name='toggle_credentials_status'),
    
    # Payment URLs
    path('', views.payment_list, name='payment_list'),
    path('<uuid:pk>/', views.payment_detail, name='payment_detail'),
    path('<uuid:pk>/mark-completed/', views.mark_payment_completed, name='mark_payment_completed'),
    path('<uuid:pk>/mark-failed/', views.mark_payment_failed, name='mark_payment_failed'),
    path('<uuid:pk>/increment-retry/', views.increment_payment_retry, name='increment_payment_retry'),
    path('status/<str:status>/', views.payment_by_status, name='payment_by_status'),
    path('method/<str:method>/', views.payment_by_method, name='payment_by_method'),
    
    # IntaSend Payment URLs
    path('intasend/initiate/', views.initiate_intasend_payment, name='initiate_intasend_payment'),
    path('intasend/<uuid:payment_id>/check-status/', views.check_intasend_payment_status, name='check_intasend_payment_status'),
    path('intasend/create-link/', views.create_intasend_payment_link, name='create_intasend_payment_link'),
    
    # Mikrotik Login Page URLs
    path('mikrotik-login/', views.mikrotik_login_page, name='mikrotik_login_page'),
    path('mikrotik-login-enhanced/', views.mikrotik_login_enhanced, name='mikrotik_login_enhanced'),
]
