#!/usr/bin/env bash

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_barbearia
python manage.py gerar_horarios
python manage.py init_admin
