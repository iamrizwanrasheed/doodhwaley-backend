"""
Django settings for doodhwaley project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import environ
from environ import Env
env = Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env(
    # set casting, default value
    # DEBUG=(bool, False)
)


def bool_env(val):
    try:
        return True if env(val) == "True" else False
    except:
        return False if val == "DEBUG" else None


# reading .env file
environ.Env.read_env(BASE_DIR + "/" + ".env")

# False if not in os.environ
DEBUG = bool_env("DEBUG")
# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")
ACCOUNT_SID = env("account_sid")
AUTH_TOKEN = env("auth_token")
MAIN_EMAIL = env("MAIN_EMAIL")
JAZZ_MERCHANT_ID = env("JAZZ_MERCHANT_ID")
JAZZ_PASSWORD = env("JAZZ_PASSWORD")
JAZZ_INTEGRITY_SECRET = env("JAZZ_INTEGRITY_SECRET")

ALLOWED_HOSTS = ["*"]
AUTH_USER_MODEL = "milkapp.User"
# Application definition
INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "milkapp",
    "django_celery_beat",
    "corsheaders",
    "rest_framework",
    "knox",
    "taggit",
]

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [  # remove
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.DjangoModelPermissions",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "knox.auth.TokenAuthentication",
    ),
    "PAGE_SIZE": 10,
}
REST_KNOX = {
    "TOKEN_TTL": None,  # default time 10h
}


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Note that this needs to be placed above CommonMiddleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_REGEX_WHITELIST = ["http://localhost:3000"]

ROOT_URLCONF = "doodhwaley.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "doodhwaley.wsgi.application"
ASGI_APPLICATION = "doodhwaley.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379")],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# if DEBUG:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#             "NAME": BASE_DIR + "/" + "db.sqlite3",
#         }
#     }
# else:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.mysql",
#             "NAME": env("DATABASE_NAME"),
#             "USER": env("DATABASE_USER"),
#             "PASSWORD": env("DATABASE_PASSWORD"),
#             "HOST": env("DB_HOST"),
#             "PORT": env("DB_PORT"),
#         },
#     }


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'doodhwaley',
#         'USER': 'root',
#         'PASSWORD': '1234',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#     }
# }
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600, ssl_require=True)
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Karachi"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILES_DIRS = [os.path.join(BASE_DIR, "milkapp/static")]
STATIC_ROOT = BASE_DIR + "/" + "staticfiles"


# Email Configurations
# SMTP Mail service with decouple
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = bool_env("EMAIL_USE_TLS")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# if not DEBUG:
#     AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
#     AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
#     AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
#     AWS_DEFAULT_ACL='public-read'

# s3 static settings
MEDIA_ROOT = BASE_DIR + "/" + "media"
MEDIA_URL = "/media/"

# if not DEBUG:
#     # For media files
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# else:
#     DEFAULT_FILE_STORAGE = 'doodhwaley.s3utils.MediaRootS3Boto3Storage'
#     STATICFILES_STORAGE = 'doodhwaley.s3utils.StaticRootS3Boto3Storage'
#     AWS_LOCATION = 'static'
#     STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/static/'
#     PUBLIC_MEDIA_LOCATION = 'media'
#     MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
# if not DEBUG:
# For media files
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# else:
#     DEFAULT_FILE_STORAGE = 'doodhwaley.s3utils.MediaRootS3Boto3Storage'
#     STATICFILES_STORAGE = 'doodhwaley.s3utils.StaticRootS3Boto3Storage'
#     AWS_LOCATION = 'static'
#     STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/static/'
#     PUBLIC_MEDIA_LOCATION = 'media'
#     MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
