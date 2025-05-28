from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fixes the SQL Explorer QueryLog table issues with NULL success values'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking SQL Explorer QueryLog table...'))
        
        with connection.cursor() as cursor:
            # First, check if the explorer_querylog table exists
            cursor.execute("""
                SELECT EXISTS (
                   SELECT FROM information_schema.tables 
                   WHERE table_name = 'explorer_querylog'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                self.stdout.write(self.style.WARNING('Table explorer_querylog does not exist yet. Skipping.'))
                return
                
            # Check if there are any NULL values in the success column
            cursor.execute("SELECT COUNT(*) FROM explorer_querylog WHERE success IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count > 0:
                self.stdout.write(self.style.WARNING(f'Found {null_count} records with NULL success values.'))
                # Update the NULL values to TRUE
                cursor.execute("UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL")
                self.stdout.write(self.style.SUCCESS(f'Updated {null_count} records with NULL success values.'))
            else:
                self.stdout.write(self.style.SUCCESS('No NULL success values found in explorer_querylog table.'))

            # Set the default value for the success column to TRUE for future inserts
            try:
                cursor.execute("""
                    ALTER TABLE explorer_querylog 
                    ALTER COLUMN success SET DEFAULT TRUE
                """)
                self.stdout.write(self.style.SUCCESS('Set DEFAULT value for success column to TRUE.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to set DEFAULT value: {str(e)}'))
                
        self.stdout.write(self.style.SUCCESS('SQL Explorer QueryLog table fix completed.')) 