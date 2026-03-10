from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('toggle-block/<int:user_id>/', views.toggle_block_user, name='toggle_block_user'),
]
