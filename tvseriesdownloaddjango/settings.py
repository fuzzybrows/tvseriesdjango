"""
Django settings for tvseriesdownloaddjango project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

DEVELOP = 'develop'

from dotenv import load_dotenv
import dj_database_url
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



ENVIRONMENT_NAME = DEVELOP

if ENVIRONMENT_NAME == DEVELOP:
    # Create .env file path.
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

    # Load file from the path.
    load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'my#@&^^7$y=lzp^2l(@szban=0l@za_#16c&ycvfo^uv9nse+b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'o2tvseries.apps.O2TvseriesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'tvseriesdownloaddjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,  'templates')],
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

WSGI_APPLICATION = 'tvseriesdownloaddjango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('PGDATABASE', ''),
        'USER': os.getenv('PGUSER', ''),
        'PASSWORD': os.getenv('PGPASSWORD', ''),
        'HOST': os.getenv('PGHOST', ''),
        'PORT': os.getenv('PGPORT', ''),
        'TEST': {
            'NAME': os.getenv('TEST_PGDATABASE', 'test_asac'),
        },
    }

}

if os.getenv('DATABASE_URL'):
    DATABASES = dict(default=dj_database_url.parse(os.getenv('DATABASE_URL'), conn_max_age=600))


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

#TEMPLATE_DIRS = (os.path.join(BASE_DIR,  'templates'),)

HOME_PATH = os.path.expanduser('~')
DOWNLOAD_PATH = "{}/Downloads/TVshows".format(HOME_PATH)
PROTOCOL = "http"
DOMAIN_NAME = "o2tvseries.com"
SOURCE_URL = "{}://{}".format(PROTOCOL, DOMAIN_NAME)
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36"
WATCHED_SHOWS = [
            'Arrow', 'Blindspot', 'Agents of shield', 'Empire', 'Gotham', 'Altered Carbon', 'Black Lightning',
            'Greys Anatomy', 'How to get away with murder',
            'Reign', 'Quantico', 'The flash',
            'Scandal', 'Hawaii', 'Supergirl', 
            'Power', 'Legends of tomorrow', 'Daredevil', 'Game of Thrones', 'Orange is the new black',
            'Jessica Jones', 'The Grand Tour', 'Designated Survivor', 'Suits'
]
