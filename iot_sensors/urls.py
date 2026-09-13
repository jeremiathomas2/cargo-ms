from django.urls import path
from . import views
app_name = 'iot_sensors'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('devices/', views.sensor_list, name='sensor_list'),
    path('devices/<uuid:pk>/', views.sensor_detail, name='sensor_detail'),
    path('alerts/', views.alert_list, name='alert_list'),
]