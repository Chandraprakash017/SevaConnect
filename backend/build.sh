#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run collectstatic
python manage.py collectstatic --no-input
