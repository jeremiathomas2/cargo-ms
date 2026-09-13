from django.urls import path
from . import views
app_name = 'risk_management'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('breaches/', views.breach_list, name='breach_list'),
    path('watchlist/', views.watchlist_list, name='watchlist_list'),
    path('risk-scores/', views.risk_score_list, name='risk_score_list'),
    path('sla-levels/', views.sla_level_list, name='sla_level_list'),
]