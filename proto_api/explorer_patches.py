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
            db_engine = connection.vendor
            logger.info(f"SQL Explorer: Applying patches for {db_engine} database")
            
            # First check if the table exists - using a more portable query
            if db_engine == 'postgresql':
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'explorer_querylog')")
                table_exists = cursor.fetchone()[0]
            elif db_engine == 'sqlite':
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='explorer_querylog'")
                table_exists = cursor.fetchone()[0] > 0
            else:
                # Generic approach for other databases
                try:
                    cursor.execute("SELECT COUNT(*) FROM explorer_querylog LIMIT 1")
                    table_exists = True
                except Exception:
                    table_exists = False
            
            if not table_exists:
                logger.info("SQL Explorer: explorer_querylog table doesn't exist yet - will be patched when created")
                return
                
            # Check for NULL values in the success column
            try:
                cursor.execute("SELECT COUNT(*) FROM explorer_querylog WHERE success IS NULL")
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    logger.info(f"SQL Explorer: Found {null_count} NULL values in success column")
                    cursor.execute("UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL")
                    logger.info(f"SQL Explorer: Updated {null_count} NULL values to TRUE")
            except Exception as e:
                logger.warning(f"SQL Explorer: Failed to check/update NULL values: {e}")
                
            # Try to set a default value for the success column based on database type
            try:
                if db_engine == 'postgresql':
                    cursor.execute("ALTER TABLE explorer_querylog ALTER COLUMN success SET DEFAULT TRUE")
                elif db_engine == 'sqlite':
                    # SQLite doesn't support ALTER COLUMN, need to use a different approach
                    # For now, we'll just rely on the middleware to catch issues
                    pass
                elif db_engine == 'mysql':
                    cursor.execute("ALTER TABLE explorer_querylog MODIFY success BOOLEAN NOT NULL DEFAULT TRUE")
                # Add other database types as needed
                
                logger.info("SQL Explorer: Set default value for success column")
            except Exception as e:
                logger.warning(f"SQL Explorer: Failed to set default for success column: {e}")
                
    except Exception as e:
        logger.warning(f"SQL Explorer: Failed to apply patches: {e}") 