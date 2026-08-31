from django.urls import path
from . import views
app_name = 'claims'
urlpatterns = [
    path('', views.claim_list, name='list'),
    path('create/<uuid:shipment_pk>/', views.claim_create, name='create'),
    path('<uuid:pk>/', views.claim_detail, name='detail'),
    path('<uuid:pk>/update/', views.claim_update_status, name='update_status'),
]
