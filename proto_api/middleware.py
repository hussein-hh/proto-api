from django.db import connection
from django.db.utils import DatabaseError
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
            except DatabaseError as e:
                error_str = str(e)
                logger.warning(f"SQL Explorer error: {error_str}")
                
                # Check if it's the specific error we're looking for
                if "null value in column \"success\"" in error_str and "explorer_querylog" in error_str:
                    logger.info("Fixing NULL success values in explorer_querylog table")
                    try:
                        with connection.cursor() as cursor:
                            # Update existing NULL success values to True
                            cursor.execute("UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL")
                            # Try to set a default value
                            cursor.execute("ALTER TABLE explorer_querylog ALTER COLUMN success SET DEFAULT TRUE")
                        
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