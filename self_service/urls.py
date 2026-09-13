from django.urls import path
from . import views
app_name = 'self_service'
urlpatterns = [
    path('', views.settings_dashboard, name='dashboard'),
    path('users/', views.user_management, name='users'),
    path('roles/', views.role_management, name='roles'),
    path('theme/', views.theme_settings, name='theme'),
    path('numbering/', views.numbering_settings, name='numbering'),
    path('shipment-templates/', views.shipment_templates, name='shipment_templates'),
    path('api-keys/', views.api_keys, name='api_keys'),
    path('bulk-uploads/', views.bulk_uploads, name='bulk_uploads'),
]
