#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Fix SQL Explorer QueryLog table directly with SQL
echo "Running SQL Explorer QueryLog fix using direct SQL"
python << EOF
import django
django.setup()
from django.db import connection

print("Checking SQL Explorer QueryLog table...")
with connection.cursor() as cursor:
    # Check if the table exists first
    cursor.execute("SELECT to_regclass('public.explorer_querylog')")
    if cursor.fetchone()[0] is None:
        print("Table explorer_querylog does not exist yet. Skipping.")
    else:
        # Fix NULL values in success column
        cursor.execute("UPDATE explorer_querylog SET success = TRUE WHERE success IS NULL")
        print("Updated any NULL success values in explorer_querylog.")
        
        # Try to set default value for the success column
        try:
            cursor.execute("ALTER TABLE explorer_querylog ALTER COLUMN success SET DEFAULT TRUE")
            print("Set DEFAULT value for success column to TRUE.")
        except Exception as e:
            print(f"Failed to set DEFAULT value: {str(e)}")
            
print("SQL Explorer QueryLog fix completed.")
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
