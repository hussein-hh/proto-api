#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Auto-create superuser if missing (email-based User model)
echo "
from django.contrib.auth import get_user_model
User = get_user_model()
# determine the USERNAME_FIELD (probably 'email')
uname_field = User.USERNAME_FIELD
admin_email = 'admin@example.com'
admin_pass = 'AdminPass123'

# only create if no user with that email exists
if not User.objects.filter(**{uname_field: admin_email}).exists():
    User.objects.create_superuser(admin_email, admin_pass)
" | python manage.py shell
