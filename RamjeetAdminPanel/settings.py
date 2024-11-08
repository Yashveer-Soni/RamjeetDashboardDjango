"""
Django settings for RamjeetAdminPanel project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from decouple import config
from decouple import Csv
from datetime import timedelta

AUTH_USER_MODEL = 'ramjeet.MyUser'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# FRONTEND_DIR = BASE_DIR / "reactfrontend"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'corsheaders',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'ramjeet',
    'ramjeetfrontend',
    'import_export',
    # 'whitenoise.runserver_nostatic'
]



MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware'
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
     'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',  # Adjust to your React app's URL
]

CORS_ALLOW_ALL_ORIGINS = True 
ROOT_URLCONF = 'RamjeetAdminPanel.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates",],
        # 'DIRS': [BASE_DIR / "static",],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]
WSGI_APPLICATION = 'RamjeetAdminPanel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        # default sql
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        # mysql
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'grocery',
        # 'USER': 'root',
        # 'PASSWORD': '',
        # 'HOST':'localhost',
        # 'PORT':'3306',
        # postgresql
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ramjeet',
        'USER': 'ramjeet',
        'HOST': 'localhost',
        'PASSWORD': 'ramjeet',
        'PORT': '5432',    
        # 
        # production database
        #  'ENGINE': 'django.db.backends.postgresql',
        #  'NAME': 'ramjeet',
        #  'USER': 'ramjeet',
        #  'HOST': config('HOST'),
        #  'PASSWORD': config('PASSWORD'),
        #  'PORT': '5432',    
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

USE_TZ = True

# LANGUAGES = [
#     ('en', _('English')),
#     ('hi', _('Hindi')),
#     # Add more languages as needed
# ]
# LOCALE_PATHS = [
#     os.path.join(BASE_DIR, 'locale'),
# ]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directory for collected static files

STATICFILES_DIRS = [
    BASE_DIR / "static",
]




# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Media files

MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media')

LOGIN_URL = '/signin/'


# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_SIGNATURE_NAME = 's3v4',
# AWS_S3_REGION_NAME = 'eu-north-1'
# AWS_S3_FILE_OVERWRITE = False
# AWS_DEFAULT_ACL =  None
# AWS_S3_VERITY = True
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),  # 1 hour for access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # 7 days for refresh token
    'ROTATE_REFRESH_TOKENS': True,                # Rotate refresh tokens on refresh
    'BLACKLIST_AFTER_ROTATION': True,             # Blacklist old refresh tokens after rotation
    'UPDATE_LAST_LOGIN': True,                    # Update the last login timestamp
    # other settings...
}
