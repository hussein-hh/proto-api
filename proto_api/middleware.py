from django.db import connection
from django.db.utils import DatabaseError, IntegrityError, OperationalError
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

class SqlExplorerMiddleware:
    """
    Middleware to handle SQL Explorer issues with QueryLog.
    This catches database errors related to the 'success' column 
    in the explorer_querylog table.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Only apply the middleware for SQL Explorer URLs
        if request.path.startswith('/explorer/'):
            try:
                # Try to execute the request normally
                return self.get_response(request)
            except (DatabaseError, IntegrityError, OperationalError) as e:
                error_str = str(e)
                logger.warning(f"SQL Explorer error: {error_str}")
                
                # Check if it's related to the success column in explorer_querylog
                if (("null value" in error_str.lower() or "not null constraint" in error_str.lower()) 
                    and "success" in error_str.lower() and "explorer_querylog" in error_str.lower()):
                    logger.info("Fixing NULL success values in explorer_querylog table")
                    try:
                        with connection.cursor() as cursor:
                            db_engine = connection.vendor
                            # Update existing NULL success values to True
                            cursor.execute("UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL")
                            
                            # Try to set a default value based on database type
                            if db_engine == 'postgresql':
                                cursor.execute("ALTER TABLE explorer_querylog ALTER COLUMN success SET DEFAULT TRUE")
                            elif db_engine == 'mysql':
                                cursor.execute("ALTER TABLE explorer_querylog MODIFY success BOOLEAN NOT NULL DEFAULT TRUE")
                            # Add other DB types as needed
                        
                        # Try again after fixing
                        logger.info("Retrying request after fixing explorer_querylog table")
                        return self.get_response(request)
                    except Exception as fix_error:
                        logger.error(f"Failed to fix explorer_querylog table: {fix_error}")
                        raise e  # Re-raise the original error
                else:
                    # If it's a different error, re-raise it
                    raise
        else:
            # For non-SQL Explorer URLs, just proceed normally
            return self.get_response(request)


class CorsFixMiddleware:
    """
    This middleware handles all CORS functionality for the API.
    It adds appropriate CORS headers to all responses and handles preflight OPTIONS requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
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
        
    def __call__(self, request):
        logger.debug(f"CorsFixMiddleware processing request: {request.method} {request.path}")
        
        # Handle OPTIONS requests first
        if request.method == 'OPTIONS':
            return self.handle_preflight(request)
            
        # For non-OPTIONS requests, process normally
        response = self.get_response(request)
        return self.add_cors_headers(request, response)
    
    def handle_preflight(self, request):
        """Handle preflight OPTIONS requests"""
        logger.debug("Handling OPTIONS preflight request")
        
        response = HttpResponse()
        response.status_code = 200  # Always return 200 for OPTIONS
        
        # Get the requested method
        requested_method = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD', '')
        logger.debug(f"Requested method: {requested_method}")
        
        # Get the requested headers
        requested_headers = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', '').lower()
        logger.debug(f"Requested headers: {requested_headers}")
        
        # Add CORS headers
        response = self.add_cors_headers(request, response)
        
        # Add specific preflight headers
        if requested_method:
            response['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
        
        if requested_headers:
            response['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
        
        return response
    
    def add_cors_headers(self, request, response):
        """Add CORS headers to a response"""
        # Get the origin from the request
        origin = request.META.get('HTTP_ORIGIN', '')
        logger.debug(f"Request origin: {origin}")
        
        # Clear any existing CORS headers to prevent duplication
        cors_headers = [key for key in response if key.lower().startswith('access-control-')]
        for header in cors_headers:
            del response[header]
            logger.debug(f"Removed existing header: {header}")
        
        # Set the allowed origin
        if origin == self.allowed_origin:
            response['Access-Control-Allow-Origin'] = origin
        else:
            response['Access-Control-Allow-Origin'] = self.allowed_origin
        
        # Add standard CORS headers
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '3600'  # 1 hour
        
        # Log the final headers
        logger.debug("Final CORS headers:")
        for header, value in response.items():
            if header.lower().startswith('access-control-'):
                logger.debug(f"{header}: {value}")
        
        return response 