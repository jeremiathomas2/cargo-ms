from django.urls import path
from . import views
app_name = 'documents'
urlpatterns = [
    path('', views.document_list, name='list'),
    path('<uuid:pk>/', views.document_detail, name='detail'),
    path('<uuid:pk>/download/', views.document_download, name='download'),
    path('generate/<str:type>/<uuid:entity_id>/', views.document_generate, name='generate'),
]
