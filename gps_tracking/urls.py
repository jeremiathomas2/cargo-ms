from django.urls import path
from . import views
app_name = 'gps_tracking'
urlpatterns = [
    path('', views.gps_dashboard, name='dashboard'),
    path('devices/', views.device_list, name='device_list'),
    path('devices/<uuid:pk>/', views.device_detail, name='device_detail'),
    path('tracking/', views.live_tracking, name='live_tracking'),
    path('geofences/', views.geofence_list, name='geofence_list'),
    path('history/', views.gps_history, name='history'),
    path('api/ingest/<str:tracker_id>/', views.gps_ingest, name='gps_ingest'),
    path('api/positions/<uuid:device_id>/', views.gps_positions_api, name='positions_api'),
]
