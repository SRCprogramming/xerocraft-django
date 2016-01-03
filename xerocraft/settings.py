"""
Django settings for xerocraft project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['XERO_DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# "This is because heroku fails to pass the headers"
SOCIAL_AUTH_REDIRECT_IS_HTTP = True

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ['GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ['GOOGLE_OAUTH2_SECRET']

SOCIAL_AUTH_TWITTER_KEY = os.environ['TWITTER_KEY']
SOCIAL_AUTH_TWITTER_SECRET = os.environ['TWITTER_SECRET']

SOCIAL_AUTH_FACEBOOK_KEY =  os.environ['FACEBOOK_KEY']
SOCIAL_AUTH_FACEBOOK_SECRET =  os.environ['FACEBOOK_SECRET']

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'xerocraft', # I'm including this for its /static folder. Any negative consequences? Use <proj>/static instead?
    'members',
    'tasks',
    'inventory',
    'djrill',
    'crispy_forms',
    'social.apps.django_app.default',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'xerocraft.authenticators.CaseInsensitiveModelBackend',
    'xerocraft.authenticators.XerocraftBackend',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.twitter.TwitterOAuth',
)

ROOT_URLCONF = 'xerocraft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'xerocraft/templates'),
            os.path.join(BASE_DIR, 'tasks/templates/')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'xerocraft.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # or django.db.backends.mysql
        'NAME': os.environ['DB_DATABASE_FOR_DJANGO'],
        'USER': os.environ['DB_USER_FOR_DJANGO'],
        'PASSWORD': os.environ['DB_PW_FOR_DJANGO'],
        'HOST': os.environ['DB_HOST_FOR_DJANGO'],
        'PORT': os.environ['DB_PORT_FOR_DJANGO']
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Arizona'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MANDRILL_API_KEY = os.environ['MANDRILL_API_KEY']
DEFAULT_FROM_EMAIL = "Volunteer Coordinator <volunteer@xerocraft.org>"


# Per http://stackoverflow.com/questions/18920428/django-logging-on-heroku

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'tasks': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'members': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'xerocraft-django': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}