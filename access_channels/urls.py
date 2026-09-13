from django.urls import path
from . import views
app_name = 'access_channels'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ussd/', views.ussd_list, name='ussd_list'),
    path('ivr/', views.ivr_list, name='ivr_list'),
    path('sync/', views.sync_queue_list, name='sync_queue_list'),
    path('translations/', views.translation_list, name='translation_list'),
]