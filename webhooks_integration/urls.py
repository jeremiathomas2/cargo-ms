from django.urls import path
from . import views
app_name = 'webhooks_integration'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('logs/', views.log_list, name='log_list'),
]