from django.urls import path
from . import views
app_name = 'cross_border'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('posts/', views.border_post_list, name='border_post_list'),
    path('declarations/', views.declaration_list, name='declaration_list'),
    path('crossings/', views.crossing_list, name='crossing_list'),
    path('corridors/', views.corridor_list, name='corridor_list'),
    path('agents/', views.agent_list, name='agent_list'),
]