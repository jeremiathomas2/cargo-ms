from django.urls import path
from . import views
app_name = 'reports'
urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('<str:report_type>/', views.report_view, name='report'),
    path('<str:report_type>/export/', views.report_export, name='export'),
]
