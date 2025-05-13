"""
WSGI config for proto_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proto_api.settings')
application = get_wsgi_application()

# This WSGI middleware only handles emergency fallback for OPTIONS requests
class CorsWsgiMiddleware:
    def __init__(self, app):
        self.app = app
        self.allowed_origin = 'https://proto-ux.netlify.app'

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            # Check if CORS headers are present
            has_cors = any(h[0].lower() == 'access-control-allow-origin' for h in headers)
            
            if not has_cors and environ.get('REQUEST_METHOD') == 'OPTIONS':
                # Only add CORS headers for OPTIONS if they're missing
                headers.extend([
                    ('Access-Control-Allow-Origin', self.allowed_origin),
                    ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE'),
                    ('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Requested-With, Origin, Accept'),
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Access-Control-Max-Age', '86400'),
                ])
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)

# Wrap the application with our CORS WSGI middleware
application = CorsWsgiMiddleware(application)
