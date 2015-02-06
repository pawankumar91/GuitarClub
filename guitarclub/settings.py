"""
Django settings for guitarclub project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w1fgxs=#&wabvz=zcbzs22vcr@e6tlg+s=9p^kv=1izq(h@!^j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'pawan.kumar.13.1991@gmail.com'
EMAIL_HOST_PASSWORD = 'P@ssw0rdP@ssw0rd'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'guitarclub.guitarclubapp',
    'guitarclubapp',
    #'django-friendship/friendship',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_DIRS = (
    '/home/pakumar1/guitarclub/templates/',
    '/home/pakumar1/guitarclub/templates/profiles/',
    '/home/pakumar1/guitarclub/templates/registration/',
    '/home/pakumar1/guitarclub/templates/search/'
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

ROOT_URLCONF = 'guitarclub.urls'

WSGI_APPLICATION = 'guitarclub.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pakumar1$dm_gc',
        'USER': 'pakumar1',
        'PASSWORD': 'P@ssw0rd',
        'HOST': 'mysql.server',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'


MEDIA_ROOT='/home/pakumar1/guitarclub/guitarclubapp/static/media/'

STATIC_ROOT = '/home/pakumar1/guitarclub/guitarclubapp/static/'

AUTH_PROFILE_MODULE= 'guitarclubapp.UserProfile'




#to redirect user to login page
import django.contrib.auth
django.contrib.auth.LOGIN_URL = '/accounts/login/'
