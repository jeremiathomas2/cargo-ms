from django.urls import path
from . import views
app_name = 'cargo'
urlpatterns = [
    path('', views.shipment_list, name='list'),
    path('create/', views.shipment_create, name='create'),
    path('<uuid:pk>/', views.shipment_detail, name='detail'),
    path('<uuid:pk>/edit/', views.shipment_edit, name='edit'),
    path('<uuid:pk>/status/', views.shipment_status_change, name='status_change'),
    path('search/', views.shipment_search, name='search'),
    path('api/search/', views.shipment_api_search, name='api_search'),
]
