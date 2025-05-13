"""
Patches for SQL Explorer models to fix issues with the original package.
This module should be imported in proto_api/__init__.py to apply the patches at startup.
"""
from django.db import connection
import logging

logger = logging.getLogger(__name__)

def apply_explorer_patches():
    """Apply patches to fix SQL Explorer issues"""
    try:
        # Try to patch the QueryLog table right away
        with connection.cursor() as cursor:
            # First check if the table exists
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'explorer_querylog')")
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                logger.info("SQL Explorer: explorer_querylog table doesn't exist yet - will be patched when created")
                return
                
            # Update success column to have a default
            cursor.execute("""
                SELECT column_default 
                FROM information_schema.columns 
                WHERE table_name = 'explorer_querylog' AND column_name = 'success'
            """)
            has_default = cursor.fetchone()[0]
            
            if not has_default:
                logger.info("SQL Explorer: Setting default value for success column")
                try:
                    cursor.execute("ALTER TABLE explorer_querylog ALTER COLUMN success SET DEFAULT TRUE")
                    # Also update any existing NULL values
                    cursor.execute("UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL")
                    logger.info("SQL Explorer: Default value for success column set to TRUE")
                except Exception as e:
                    logger.warning(f"SQL Explorer: Failed to set default for success column: {e}")
            else:
                logger.info("SQL Explorer: success column already has a default value")
                
    except Exception as e:
        logger.warning(f"SQL Explorer: Failed to apply patches: {e}") 