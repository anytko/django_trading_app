#!/bin/bash

# Install required dependencies
pip install -r requirements.txt

# Run Django management commands
python manage.py collectstatic --noinput