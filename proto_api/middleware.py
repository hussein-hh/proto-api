from django.db import connection
from django.db.utils import DatabaseError, IntegrityError, OperationalError
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
        
    def __call__(self, request):
        logger.debug(f"CorsFixMiddleware processing request: {request.method} {request.path}")
        
        # Special handling for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            logger.debug("Handling OPTIONS preflight request")
            return self.handle_preflight(request)
        
        # Process the request and get the response
        response = self.get_response(request)
        
        # Add CORS headers to all responses
        return self.add_cors_headers(request, response)
    
    def handle_preflight(self, request):
        """Handle preflight OPTIONS requests"""
        from django.http import HttpResponse
        
        response = HttpResponse()
        response.status_code = 200
        return self.add_cors_headers(request, response)
    
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
        
        # Always set the allowed origin header
        if origin == self.allowed_origin:
            response['Access-Control-Allow-Origin'] = origin
        else:
            response['Access-Control-Allow-Origin'] = self.allowed_origin
        
        # Add the other CORS headers
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, X-Requested-With, Origin, Accept'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        # Log the final headers for debugging
        logger.debug("Final CORS headers:")
        for header, value in response.items():
            if header.lower().startswith('access-control-'):
                logger.debug(f"{header}: {value}")
        
        return response 