from django.db import connection
from django.db.utils import DatabaseError


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
                # Check if it's the specific error we're looking for
                error_str = str(e)
                if "null value in column \"success\"" in error_str and "explorer_querylog" in error_str:
                    # If it's a QueryLog success field error, apply a patch to the database
                    with connection.cursor() as cursor:
                        # Update existing NULL success values to True
                        cursor.execute("UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL")
                    
                    # Try again after fixing
                    return self.get_response(request)
                else:
                    # If it's a different error, re-raise it
                    raise
        else:
            # For non-SQL Explorer URLs, just proceed normally
            return self.get_response(request) 