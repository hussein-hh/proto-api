#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Fix SQL Explorer QueryLog table directly with SQL using django-admin
echo "Running SQL Explorer QueryLog fix using direct SQL"
python - << EOF
import os
import sys

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proto_api.settings')
# Add the current directory to the Python path
sys.path.append('.')

# Now import Django and set it up
import django
django.setup()

# After Django is set up, we can safely import and use Django components
from django.db import connection
print("Checking SQL Explorer QueryLog table...")

# Function to safely execute SQL
def safe_execute(cursor, sql, params=None):
    try:
        cursor.execute(sql, params or ())
        return True
    except Exception as e:
        print(f"SQL Error: {e}")
        return False

with connection.cursor() as cursor:
    # Check if the table exists using a more portable query
    safe_execute(cursor, "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'explorer_querylog'")
    result = cursor.fetchone()
    
    if result and result[0] > 0:
        print("Table explorer_querylog exists - checking for NULL success values")
        
        # Check for NULL success values
        if safe_execute(cursor, "SELECT COUNT(*) FROM explorer_querylog WHERE success IS NULL"):
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                print(f"Found {null_count} records with NULL success values")
                if safe_execute(cursor, "UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL"):
                    print(f"Updated {null_count} records with NULL success values")
            else:
                print("No NULL success values found")
        
        # Try to set default value
        if safe_execute(cursor, """
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'explorer_querylog' 
              AND column_name = 'success' 
              AND column_default IS NULL
        """):
            needs_default = cursor.fetchone()[0] > 0
            if needs_default:
                print("Setting DEFAULT TRUE for success column")
                if safe_execute(cursor, "ALTER TABLE explorer_querylog ALTER COLUMN success SET DEFAULT TRUE"):
                    print("Successfully set DEFAULT value for success column")
            else:
                print("Success column already has a default value")
    else:
        print("Table explorer_querylog does not exist yet - it will be created during migration")

print("SQL Explorer QueryLog fix completed")
EOF

# Auto-create superuser if missing (for Auth.User model)
echo "
from Domains.Auth.models import User
admin_email = 'admin@example.com'
admin_password = 'AdminPass123'

# Only create if no superuser exists
if not User.objects.filter(email=admin_email).exists():
    try:
        user = User.objects.create_superuser(email=admin_email, password=admin_password)
        print(f'Superuser {admin_email} created successfully!')
    except Exception as e:
        print(f'Failed to create superuser: {str(e)}')
else:
    print(f'Superuser {admin_email} already exists.')
" | python manage.py shell
