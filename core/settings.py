import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# READING ENV
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))  # .env faylini o'qish

# SECURITY
SECRET_KEY = env.str("SECRET_KEY")  # Yashirin kalit .env dan
DEBUG = env.bool("DEBUG", default=False)  # DEBUG holati .env dan
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # ALLOWED_HOSTS .env dan

# Application definition
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.bot'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Database
DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE"),  # DB engine .env dan
        "NAME": env.str("DB_NAME"),  # DB nomi .env dan
        "USER": env.str("DB_USER"),  # DB foydalanuvchi .env dan
        "PASSWORD": env.str("DB_PASSWORD"),  # DB parol .env dan
        "HOST": env.str("DB_HOST"),  # DB host .env dan
        "PORT": env.str("DB_PORT"),  # DB port .env dan
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
