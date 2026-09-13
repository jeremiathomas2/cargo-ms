from django.urls import path
from . import views
app_name = 'saas_config'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/<uuid:pk>/', views.organization_detail, name='organization_detail'),
]