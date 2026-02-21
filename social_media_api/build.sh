#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=social_media_api.settings_production python manage.py collectstatic --no-input
DJANGO_SETTINGS_MODULE=social_media_api.settings_production python manage.py migrate
