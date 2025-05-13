from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import HttpResponse

# Simple health check view
def health_check(request):
    return HttpResponse("API is running", content_type="text/plain")

urlpatterns = [
    # Root URL redirects to admin
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    # Admin and other endpoints
    path('admin/', admin.site.urls),
    path('auth/', include('Domains.Auth.urls')),  
    path('upload/', include('Domains.ManageData.urls')), 
    path('onboard/', include('Domains.Onboard.urls')),
    path('ask-ai/', include('Domains.Results.urls')),  
    path('toolkit/', include('Domains.Toolkit.urls')),
    path('explorer/', include('explorer.urls')),
]
