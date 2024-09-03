from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(iqbq_5^=axvh6+)6+lov0!t8&z%#h7s4ebd7-qn#aau0-#!2a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'backend.apps.BackendConfig',
    'django_countries',
    'rest_framework',
    'storages',
]

AUTH_USER_MODEL = 'backend.User'

MIDDLEWARE = [
    'backend.middleware.UserLocationMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'website.urls'

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
                'backend.context_processors.TotalDeposit',
                'backend.context_processors.PendingWithdrawal',
                'backend.context_processors.TotalWithdrawal',
                'backend.context_processors.ActiveDeposit',
                'backend.context_processors.Notify',
                'backend.context_processors.Message',
                'backend.context_processors.ActiveEarnings',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'




# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    'default': dj_database_url.parse(os.getenv('banking'))
}



#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',  # or another database backend like 'django.db.backends.postgresql'
#        'NAME': BASE_DIR / "db.sqlite3",  # for SQLite
#        # or for PostgreSQL
#        # 'NAME': 'your_database_name',
#        # 'USER': 'your_database_user',
#        # 'PASSWORD': 'your_database_password',
#        # 'HOST': 'localhost',
#        # 'PORT': '5432',
#    }
#}


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

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_FILES = [
    os.path.join(BASE_DIR, 'static')
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#AWS_STORAGE_BUCKET_NAME = 'kwexbanking'
#AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
#STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST='mail.finovaedge.com'
EMAIL_PORT =587
EMAIL_HOST_USER='support@finovaedge.com'
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS =True
DEFAULT_FROM_EMAIL ='support@finovaedge.com'

LOGIN_REDIRECT_URL = ('/Profile-dashboard')
LOGOUT_REDIRECT_URL = ('/')
SESSION_EXPIRE_AT_BROWSER_CLOSE = True