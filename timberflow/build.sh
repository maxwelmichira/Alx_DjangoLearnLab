#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=timberflow.settings_production python manage.py collectstatic --no-input
DJANGO_SETTINGS_MODULE=timberflow.settings_production python manage.py migrate
DJANGO_SETTINGS_MODULE=timberflow.settings_production python manage.py seed_demo_data
