from django.urls import path
from . import views
app_name = 'payments'
urlpatterns = [
    path('', views.payment_list, name='list'),
    path('<uuid:pk>/', views.payment_detail, name='detail'),
    path('create/<uuid:invoice_pk>/', views.payment_create, name='create'),
    path('webhook/', views.payment_webhook, name='webhook'),
]
