from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('forget-password/',views.forget_password,name='forget_password'),
    path('new-password/',views.new_password,name='new_password'),
    # path('verify-otp/', views.verify_otp, name='verify_otp'),
    # path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('profile/',views.profile,name='profile'),
    path('profile/edit-profile/',views.edit_profile,name='edit_profile'),
]
