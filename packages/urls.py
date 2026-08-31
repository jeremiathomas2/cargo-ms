from django.urls import path
from . import views
app_name = 'packages'
urlpatterns = [
    path('', views.package_list, name='list'),
    path('<uuid:pk>/', views.package_detail, name='detail'),
    path('<uuid:pk>/scan/', views.package_scan, name='scan'),
    path('<uuid:pk>/move/', views.package_move, name='move'),
]
