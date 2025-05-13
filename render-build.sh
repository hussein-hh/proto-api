#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Fix SQL Explorer QueryLog table
echo "Running SQL Explorer QueryLog fix"
python manage.py fix_explorer_querylog

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
