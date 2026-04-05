#!/usr/bin/env bash
# Render build script — runs before every deploy

set -o errexit   # exit on any error

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Seed database with books (skips existing books automatically)
python manage.py seed_books --books 15
