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
    Custom middleware to ensure CORS headers are added even in case of errors.
    This addresses issues with CORS headers not being added by Django CORS headers
    middleware in certain scenarios.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CORS headers to all responses from specific paths
        # These are paths where we know CORS errors are happening
        if request.path.startswith('/toolkit/web-metrics/'):
            origin = request.META.get('HTTP_ORIGIN')
            
            # If an origin was specified, add it to the allow origin header
            if origin:
                response["Access-Control-Allow-Origin"] = origin
            else:
                # Fallback to the main frontend domain if no origin was specified
                response["Access-Control-Allow-Origin"] = "https://proto-ux.netlify.app"
                
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "authorization, content-type, origin, x-csrftoken"
            response["Access-Control-Allow-Credentials"] = "true"
            
        return response 