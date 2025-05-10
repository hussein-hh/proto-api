#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

