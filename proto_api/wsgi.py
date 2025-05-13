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

# This WSGI middleware is a fallback to ensure CORS works in any case
# It's simpler now because the main CorsFixMiddleware does most of the work
class CorsWsgiMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Handle OPTIONS preflight requests immediately at the WSGI level
        if environ.get('REQUEST_METHOD') == 'OPTIONS' and '/toolkit/web-metrics/' in environ.get('PATH_INFO', ''):
            response_headers = [
                ('Content-Type', 'text/plain'),
                ('Access-Control-Allow-Origin', environ.get('HTTP_ORIGIN', 'https://proto-ux.netlify.app')),
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE'),
                ('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Requested-With, Origin, Accept'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Max-Age', '86400'),
            ]
            start_response('200 OK', response_headers)
            return [b'']

        return self.app(environ, start_response)

# Wrap the application with our CORS WSGI middleware
application = CorsWsgiMiddleware(application)
