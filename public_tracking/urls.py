from django.urls import path
from . import views
app_name = 'public_tracking'
urlpatterns = [
    path('', views.tracking_home, name='home'),
    path('<str:tracking_id>/', views.tracking_result, name='result'),
]
