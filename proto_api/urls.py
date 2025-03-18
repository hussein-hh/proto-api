from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Domains.Auth.urls')),  
    path('upload/', include('Domains.ManageData.urls')), 
    path('onboard/', include('Domains.Onboard.urls')),
    path('ask-ai/', include('Domains.Results.urls')),  
]
