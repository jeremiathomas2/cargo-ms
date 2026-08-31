from django.urls import path
from . import views
app_name = 'transportation'
urlpatterns = [
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<uuid:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/<uuid:pk>/', views.driver_detail, name='driver_detail'),
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/<uuid:pk>/', views.trip_detail, name='trip_detail'),
    path('manifests/', views.manifest_list, name='manifest_list'),
    path('manifests/<uuid:pk>/', views.manifest_detail, name='manifest_detail'),
    path('routes/', views.route_list, name='route_list'),
]
