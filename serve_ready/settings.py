from pathlib import Path
from dotenv import load_dotenv
import os

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# Безопасное получение переменных окружения
def get_env_variable(var_name, default=None):
    """Получить переменную окружения или использовать значение по умолчанию"""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

# Используем переменные окружения для безопасности
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY', '2JyYgDagv9KU3qB60dLSVWgr0qO4wDfEd1+7KbeffVM=')

DEBUG = get_env_variable('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = get_env_variable('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Настройки базы данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_variable('DB_NAME', 'serve_ready_db'),
        'USER': get_env_variable('DB_USER', 'serve_ready_user'),
        'PASSWORD': get_env_variable('DB_PASSWORD', '4689'),
        'HOST': get_env_variable('DB_HOST', 'localhost'),
        'PORT': get_env_variable('DB_PORT', '5432'),
        'OPTIONS': {
            # Рекомендуемые настройки для производительности
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,  # Поддержание соединения 10 минут
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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

ROOT_URLCONF = 'serve_ready.urls'

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

WSGI_APPLICATION = 'serve_ready.wsgi.application'

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

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

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'index'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'