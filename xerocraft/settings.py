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
import uuid

DEVHOSTS = [
    238402988951122,  # Adrian Linux
    220083055528387,  # Adrian Mac
]
CURRHOST = uuid.getnode()
ISDEVHOST = CURRHOST in DEVHOSTS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
#STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['XERO_DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if ISDEVHOST else False

ALLOWED_HOSTS = (
    'xerocraft-django.herokuapp.com',
    'xis.xerocraft.us',
)
if ISDEVHOST:
    ALLOWED_HOSTS += (
        'localhost',
    )

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Forcing social auth redirect to HTTPS fixes social auth inside Xerocraft, where HTTPS is used.
# However, it breaks social auth outside Xerocraft, where HTTP is used.
# Social auth would work inside AND outside if we replace reverse proxy inside XC with Heroku's SSL.
# That said, I'm not sure that access outside Xerocraft should be allowed at all.
# BTW, one Stack Exchange comment blames Heroku: "This is because heroku fails to pass the headers"

# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ['GOOGLE_OAUTH2_KEY']
# SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ['GOOGLE_OAUTH2_SECRET']

# SOCIAL_AUTH_TWITTER_KEY = os.environ['TWITTER_KEY']
# SOCIAL_AUTH_TWITTER_SECRET = os.environ['TWITTER_SECRET']

# SOCIAL_AUTH_FACEBOOK_KEY =  os.environ['FACEBOOK_KEY']
# SOCIAL_AUTH_FACEBOOK_SECRET =  os.environ['FACEBOOK_SECRET']

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Req'd by helpdesk
    'django.contrib.humanize',  # Req'd by helpdesk
)

if ISDEVHOST:
    # Django-Jenkins docs say to list it as soon as possible after django modules,
    # So I'm putting all the development and WIP stuff here.
    INSTALLED_APPS += (
        'django_jenkins',
        #'debug_toolbar',
    )

INSTALLED_APPS += (
    'abutils',
    'xerocraft', # I'm including this for its /static folder. Any negative consequences? Use <proj>/static instead?
    'members',
    'tasks',
    'inventory',
    'crispy_forms',
    'social.apps.django_app.default',
    'rest_framework',
    'rest_framework.authtoken',
    'books',
    'reversion',
    'modelmailer',

    'markdown_deux',  # for helpdesk
    'bootstrapform',  # for helpdesk
    'helpdesk',
)

SITE_ID = 1  # For django.contrib.sites

MIDDLEWARE_CLASSES = (
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

SESSION_COOKIE_AGE = 10*60
SESSION_SECURITY_WARN_AFTER = 9*60
SESSION_SAVE_EVERY_REQUEST = True


AUTHENTICATION_BACKENDS = (
    'xerocraft.authenticators.CaseInsensitiveModelBackend',
    'xerocraft.authenticators.XerocraftBackend',
    # 'social.backends.facebook.FacebookOAuth2',
    # 'social.backends.google.GoogleOAuth2',
    # 'social.backends.twitter.TwitterOAuth',
)
if ISDEVHOST:
    AUTHENTICATION_BACKENDS += (
    )

ANONYMOUS_USER_ID = -1

ROOT_URLCONF = 'xerocraft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'xerocraft/templates'),
            os.path.join(BASE_DIR, 'tasks/templates/'),
            os.path.join(BASE_DIR, 'members/templates/'),
            os.path.join(BASE_DIR, 'inventory/templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
                # 'social.apps.django_app.context_processors.backends',
                # 'social.apps.django_app.context_processors.login_redirect',
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

from django.conf.locale.en import formats as en_formats
en_formats.DATETIME_FORMAT = "m/d/y H:i:s"
en_formats.DATE_FORMAT = "m/d/y"


# EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# MANDRILL_API_KEY = os.environ['MANDRILL_API_KEY']

EMAIL_BACKEND = "sparkpost.django.email_backend.SparkPostEmailBackend"
SPARKPOST_API_KEY = os.environ['SPARKPOST_API_KEY']
DEFAULT_FROM_EMAIL = "Xerocraft Systems <xis@xerocraft.org>"
SPARKPOST_OPTIONS = {
    'track_opens': False,
    'track_clicks': False,
    'transactional': True,
}

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
        'modelmailer': {
            'handlers': ['console'],
            'level': 'INFO',
        },
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser'
    ],

    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.DjangoFilterBackend',
    ],

    'PAGE_SIZE': 100
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    }
}

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# JENKINS

PROJECT_APPS = ('abutils', 'books', 'inventory', 'members', 'modelmailer', 'tasks', 'xerocraft')

JENKINS_TASKS = (
    # 'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.run_pyflakes',
    # 'django_jenkins.tasks.run_jslint',
    # 'django_jenkins.tasks.run_csslint',
    'django_jenkins.tasks.run_sloccount'
)

PYLINT_LOAD_PLUGIN = (
    'pylint_django',
)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# IntSys Config
#
# Using "IntSys" as a generic non-Xerocraft-specific name for the project.
# The system is called "Xerocraft Internal Systems" (XIS) at Xerocraft.
#
# Configuration of IntSys for Xerocraft follows. Change for your organization.

INTSYS_SYS_NAME = "XIS"

INTSYS_ORG_NAME = "Xerocraft"
INTSYS_ORG_NAME_POSSESSIVE = "Xerocraft's"

# Set the INTSYS_FACILITY_PUBLIC_IP environment variable to either:
#   (1) A DNS name that resolves to the facility's public IP
#   (2) The facility's static IP address.
INTSYS_FACILITY_PUBLIC_IP = os.getenv('INTSYS_FACILITY_PUBLIC_IP', None)
