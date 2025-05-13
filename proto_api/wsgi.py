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

# WSGI middleware for CORS handling
class CorsWsgiMiddleware:
    def __init__(self, app):
        self.app = app
        self.allowed_origin = 'https://proto-ux.netlify.app'
        self.allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
        self.allowed_headers = [
            'accept',
            'accept-encoding',
            'authorization',
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
        ]

    def __call__(self, environ, start_response):
        # Handle OPTIONS requests at WSGI level
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            return self.handle_options(environ, start_response)

        def custom_start_response(status, headers, exc_info=None):
            # Ensure CORS headers are present
            cors_headers = []
            has_origin = False
            
            # Check existing headers
            for name, value in headers:
                if name.lower() == 'access-control-allow-origin':
                    has_origin = True
            
            # Add CORS headers if missing
            if not has_origin:
                cors_headers = [
                    ('Access-Control-Allow-Origin', self.allowed_origin),
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Access-Control-Allow-Methods', ', '.join(self.allowed_methods)),
                    ('Access-Control-Allow-Headers', ', '.join(self.allowed_headers)),
                    ('Access-Control-Max-Age', '3600'),
                ]
            
            headers.extend(cors_headers)
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)

    def handle_options(self, environ, start_response):
        # Always return 200 OK for OPTIONS with CORS headers
        headers = [
            ('Content-Type', 'text/plain'),
            ('Access-Control-Allow-Origin', self.allowed_origin),
            ('Access-Control-Allow-Methods', ', '.join(self.allowed_methods)),
            ('Access-Control-Allow-Headers', ', '.join(self.allowed_headers)),
            ('Access-Control-Allow-Credentials', 'true'),
            ('Access-Control-Max-Age', '3600'),
        ]
        start_response('200 OK', headers)
        return [b'']

# Wrap the application with our CORS WSGI middleware
application = CorsWsgiMiddleware(application)
