from django.urls import path
from . import views
app_name = 'delivery'
urlpatterns = [
    path('', views.delivery_list, name='list'),
    path('<uuid:pk>/', views.delivery_detail, name='detail'),
    path('<uuid:pk>/pod/', views.proof_of_delivery, name='pod'),
    path('<uuid:pk>/attempt/', views.delivery_attempt, name='attempt'),
]
