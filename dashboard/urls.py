from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [
    path('', views.index, name='index'),
    path('operations/', views.operations, name='operations'),
    path('transportation/', views.transportation_dashboard, name='transportation'),
    path('finance/', views.finance_dashboard, name='finance'),
]
