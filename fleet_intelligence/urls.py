from django.urls import path
from . import views
app_name = 'fleet_intelligence'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('scorecards/', views.scorecard_list, name='scorecard_list'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('fuel/', views.fuel_log_list, name='fuel_log_list'),
    path('emissions/', views.emission_list, name='emission_list'),
]