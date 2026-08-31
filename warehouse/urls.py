from django.urls import path
from . import views
app_name = 'warehouse'
urlpatterns = [
    path('', views.warehouse_list, name='list'),
    path('<uuid:pk>/', views.warehouse_detail, name='detail'),
    path('<uuid:pk>/receiving/', views.warehouse_receiving, name='receiving'),
    path('<uuid:pk>/dispatch/', views.warehouse_dispatch, name='dispatch'),
    path('<uuid:pk>/movements/', views.warehouse_movements, name='movements'),
    path('<uuid:pk>/zones/', views.warehouse_zones, name='zones'),
]
