from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('userlist/', views.user_list, name='user_list'),
    path('sales-report/',views.admin_sales_report,name='admin_sales_report'),
    path('toggle-block/<int:user_id>',views.toggle_block_user,name='toggle_block_user'),
]
