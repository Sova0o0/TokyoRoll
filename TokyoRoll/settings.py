"""
Django settings for TokyoRoll project.
"""

import os
import sys
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Используй переменную окружения в продакшене, для локальной разработки - ключ ниже
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-menbz(f65g@mplqk6*78)ogzpjkf5pb14yw@nju28d9vn3**2y')

# SECURITY WARNING: don't run with debug turned on in production!
# Для продакшена DEBUG должен быть False, для локальной разработки - True
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Разрешённые хосты
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'tokyoroll.onrender.com',      # Основной домен на Render
    'tokyoroll.vercel.app'         # Основной домен на Vercel
    '.onrender.com',               # Добавит все *.onrender.com адреса
    'www.tokyoroll.onrender.com',
]

# CSRF доверенные источники
CSRF_TRUSTED_ORIGINS = [
    'https://127.0.0.1',
    'https://localhost',
    'tokyoroll.vercel.app',
    'https://tokyoroll.onrender.com',
    'https://tokyoroll.ru',
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'main',        
    'orders',
    'cart', 
    'accounts',
    'bot',
    'admin_panel',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise для статики
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "TokyoRoll.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],  # Добавляем глобальную папку шаблонов
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "TokyoRoll.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Поддержка PostgreSQL через переменную окружения DATABASE_URL
# Для локальной разработки используется SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Если задана переменная DATABASE_URL, используем её (для PostgreSQL на Render/Railway)
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "ru-ru"  # Меняем на русский
TIME_ZONE = "Europe/Moscow"  # Меняем часовой пояс на Московский
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise для сжатия и кэширования статики
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (загруженные пользователями файлы)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security settings for production
if not DEBUG:
    # HTTPS настройки
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Для разработки - автоматически включаем DEBUG при runserver
if 'runserver' in sys.argv:
    DEBUG = True
    # Отключаем HTTPS для локальной разработки
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}