from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('system-admin/', admin.site.urls),
    path('',include('home.urls'),name='home'),
    path('user/', include('accounts.urls')),
    path('admin/',include('adminpanel.urls')),
]
