from django.urls import path
from . import views
app_name = 'branches'
urlpatterns = [
    path('', views.branch_list, name='list'),
    path('create/', views.branch_create, name='create'),
    path('<uuid:pk>/', views.branch_detail, name='detail'),
    path('<uuid:pk>/edit/', views.branch_edit, name='edit'),
]
