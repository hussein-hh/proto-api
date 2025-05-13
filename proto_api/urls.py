from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import HttpResponse
import traceback

# Simple health check view
def health_check(request):
    return HttpResponse("API is running", content_type="text/plain")

# Explorer debug view
def explorer_debug(request):
    try:
        # Try to import the Explorer views
        from explorer.views import QueryListView
        
        # Try to check database connection
        from django.db import connections
        conn = connections['default']
        conn.cursor()
        
        # If we get here, basic functionality is working
        return HttpResponse(
            "Explorer diagnostic check passed. Try accessing /explorer/ now.<br>"
            "If you still see errors, check the server logs for details.",
            content_type="text/html"
        )
    except Exception as e:
        # Return detailed error information
        error_details = traceback.format_exc()
        return HttpResponse(
            f"Explorer diagnostic failed:<br><pre>{e}\n\nTraceback:\n{error_details}</pre>",
            content_type="text/html",
            status=500
        )

urlpatterns = [
    # Root URL redirects to admin
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    # Explorer debug endpoint
    path('explorer-debug/', explorer_debug, name='explorer_debug'),
    
    # Admin and other endpoints
    path('admin/', admin.site.urls),
    path('auth/', include('Domains.Auth.urls')),  
    path('upload/', include('Domains.ManageData.urls')), 
    path('onboard/', include('Domains.Onboard.urls')),
    path('ask-ai/', include('Domains.Results.urls')),  
    path('toolkit/', include('Domains.Toolkit.urls')),
    path('explorer/', include('explorer.urls')),
]
