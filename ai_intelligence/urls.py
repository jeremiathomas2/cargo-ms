from django.urls import path
from . import views
app_name = 'ai_intelligence'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('eta/', views.eta_list, name='eta_list'),
    path('anomalies/', views.anomaly_list, name='anomaly_list'),
    path('optimizations/', views.optimization_list, name='optimization_list'),
    path('pricing/', views.pricing_list, name='pricing_list'),
]