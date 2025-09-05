#!/usr/bin/env bash
set -o errexit

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Migraciones y estáticos
python manage.py collectstatic --no-input
python manage.py migrate
