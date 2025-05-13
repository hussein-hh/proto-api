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

# Add CORS middleware at the WSGI level to ensure it's applied to all responses
class CorsWsgiMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def cors_start_response(status, headers, exc_info=None):
            # Check if this is a request from the frontend
            origin = environ.get('HTTP_ORIGIN')
            path_info = environ.get('PATH_INFO', '')
            
            # Convert headers to a dict for easier manipulation
            headers_dict = dict(headers)
            
            # Add CORS headers for web-metrics endpoints specifically
            if '/toolkit/web-metrics/' in path_info:
                # Only add headers if they don't already exist
                if 'Access-Control-Allow-Origin' not in headers_dict:
                    # Set the CORS origin header based on the request origin
                    if origin:
                        headers.append(('Access-Control-Allow-Origin', origin))
                    else:
                        headers.append(('Access-Control-Allow-Origin', 'https://proto-ux.netlify.app'))
                
                if 'Access-Control-Allow-Methods' not in headers_dict:
                    headers.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'))
                
                if 'Access-Control-Allow-Headers' not in headers_dict:
                    headers.append(('Access-Control-Allow-Headers', 'authorization, content-type, origin, x-csrftoken'))
                
                if 'Access-Control-Allow-Credentials' not in headers_dict:
                    headers.append(('Access-Control-Allow-Credentials', 'true'))
                
            return start_response(status, headers, exc_info)

        # Handle OPTIONS requests directly at the WSGI level
        if environ.get('REQUEST_METHOD') == 'OPTIONS' and '/toolkit/web-metrics/' in environ.get('PATH_INFO', ''):
            response_headers = [
                ('Content-Type', 'text/plain'),
                ('Access-Control-Allow-Origin', environ.get('HTTP_ORIGIN', 'https://proto-ux.netlify.app')),
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'authorization, content-type, origin, x-csrftoken'),
                ('Access-Control-Allow-Credentials', 'true'),
            ]
            start_response('200 OK', response_headers)
            return [b'']

        return self.app(environ, cors_start_response)

# Wrap the application with our CORS WSGI middleware
application = CorsWsgiMiddleware(application)
