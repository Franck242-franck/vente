"""
Django settings for gestion_produits project.
Adapté pour Render et Railway avec PostgreSQL et CSRF sécurisé.
"""

from pathlib import Path
from decouple import config
import dj_database_url
import os

# ===========================
# BASE
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# SECRET KEY
# ===========================
SECRET_KEY = config('SECRET_KEY')

# ===========================
# DEBUG (variable d'environnement)
# ===========================
DEBUG = config('DEBUG', default=False, cast=bool)

# ===========================
# ALLOWED HOSTS
# ===========================
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=lambda v: [x.strip() for x in v.split(',')]
)

# ===========================
# CSRF TRUSTED ORIGINS
# ===========================
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [x.strip() for x in v.split(',')] if v else []
)

# ===========================
# INSTALLED APPS
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'produits',  # ton app
    # DRF + JWT
    'rest_framework',
    'rest_framework_simplejwt',
    # CORS
    'corsheaders',
]

# ===========================
# MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================
# URLS & TEMPLATES
# ===========================
ROOT_URLCONF = 'gestion_produits.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_produits.wsgi.application'

# ===========================
# DATABASE
# ===========================
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# ===========================
# PASSWORD VALIDATION
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ===========================
# INTERNATIONALIZATION
# ===========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================
# STATIC FILES
# ===========================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Ajoutez ces lignes après STATICFILES_DIRS
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_INDEX_FILE = True  # Pour servir index.html automatiquement

# ===========================
# AUTH REDIRECTION
# ===========================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ===========================
# REST FRAMEWORK
# ===========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# ===========================
# CORS
# ===========================
CORS_ALLOW_ALL_ORIGINS = True  # pour tests, restreindre en prod

# ===========================
# NOTES
# ===========================
# - DEBUG, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS doivent être définis via variables d'environnement sur Render et Railway
# - DATABASE_URL doit être défini sur Railway (PostgreSQL) ou Render
