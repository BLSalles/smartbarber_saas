
import os
from pathlib import Path
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-smartwash-key'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'agendamento',
    "jazzmin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
]

JAZZMIN_SETTINGS = {
    "site_title": "SmartWash Admin",
    "site_header": "SmartWash",
    "site_brand": "SmartRoutine",
    "welcome_sign": "Bem-vindo ao painel",
    "copyright": "SmartRoutine",

    # logo no topo (admin)
    "site_logo": "agendamento/logo-icon.png",
    "site_logo_classes": "img-circle",
    "site_icon": "agendamento/logo-icon.png",

    # menu lateral
    "show_sidebar": True,
    "navigation_expanded": True,

    # ícones (Bootstrap Icons / FontAwesome)
    "icons": {
        "auth.user": "bi bi-people",
        "auth.Group": "bi bi-shield-lock",
        "agendamento.Agendamento": "bi bi-calendar-check",
        "agendamento.TipoLavagem": "bi bi-tags",
    },

    # ordem do menu
    "order_with_respect_to": [
        "agendamento",
        "agendamento.Agendamento",
        "agendamento.TipoLavagem",
        "auth",
        "auth.user",
        "auth.Group",
    ],

    # deixa mais limpo
    "topmenu_links": [
        {"name": "Site", "url": "/", "new_window": True},
        {"model": "auth.User"},
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
]

ROOT_URLCONF = 'smartwash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # ✅ importante
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smartwash.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

