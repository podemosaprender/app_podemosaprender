"""
Django settings for pa_site project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

ES_HEROKU= False
try:
	import django_heroku #U: autoconfiguracion Heroku, comando complementario al final del archivo
	ES_HEROKU= True
except ImportError:
	print('django_heroku no esta disponible')

from pa_lib_py.util import * #U: para cargar config via json
from pathlib import Path
from datetime import timedelta
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(f'Reading .env from {str(BASE_DIR)}')
CFG= json_to_env('.env',str(BASE_DIR))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CFG['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
IS_DEVEL_SERVER= CFG.get('IS_PROD', (len(sys.argv)>1 and sys.argv[1] == 'runserver'))
DEBUG = CFG.get('DEBUG', IS_DEVEL_SERVER)

ALLOWED_HOSTS = CFG.get('ALLOWED_HOSTS', #U: SEC: restringir en Produccion
	['localhost', '127.0.0.1', '.pythonanywhere.com', '.podemosaprender.org']
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', #U: tambien lo requiere graphene_django

	  'django_filters', #U: filtrar querysets con parametros de url #VER: https://django-filter.readthedocs.io/en/stable/

    'django_extensions', #U: runserver_plus con httpS para Facebook

    'bootstrap4', #U: tags que generan codigo bootstrap ej para forms

    'social_django', #U: autenticacion con facebook, google 

    'corsheaders', #U: headers para que la API REST/GraphQL se pueda consumir desde otras paginas

    'rest_framework', #U: atendemos pedidos REST

    'rest_framework_simplejwt.token_blacklist', #VER: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/blacklist_app.html

    'graphene_django', #U: GraphQL en vez de rest, #VER: https://docs.graphene-python.org/projects/django/en/latest/installation/

    'pa_charlas_app.apps.PaCharlasAppConfig', #A: la app de charlas de PodemosAprender
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',#U: para que la API REST se pueda consumir desde otras paginas
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pa_site.urls'

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

WSGI_APPLICATION = 'pa_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
Database={ #DFLT
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

if not CFG.get('DB') is None:
	Database= CFG.get('DB')

DATABASES = {
    'default': Database
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.instagram.InstagramOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT= CFG.get('STATIC_PATH',os.path.join(BASE_DIR, 'static'))
print(f'STATIC FILES AT {STATIC_ROOT}')

MEDIA_ROOT= CFG.get('UPLOADED_PATH', os.path.join(BASE_DIR,'www/deusr')) #U: donde suben las imagenes via upload
os.makedirs(MEDIA_ROOT, exist_ok=True) #A: creamos el dir si no existia
MEDIA_URL= 'deusr/' #U: url donde se muestran las imagenes subidas
#VER: https://docs.djangoproject.com/en/3.2/ref/settings/#file-upload-settings


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'

SOCIAL_AUTH_FACEBOOK_KEY= CFG['SOCIAL_AUTH_FACEBOOK_KEY'] #U: de la consola de desarrollo de facebook, app id
SOCIAL_AUTH_FACEBOOK_SECRET= CFG['SOCIAL_AUTH_FACEBOOK_SECRET'] #U: consola de fb, en settings, basic

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = CFG['SOCIAL_AUTH_GOOGLE_KEY'] #U: de la consola de google
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = CFG['SOCIAL_AUTH_GOOGLE_SECRET']

import os

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
        'level': 'DEBUG',
    },
}


#S: servicios rest
REST_FRAMEWORK = {
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
	#VER: https://www.django-rest-framework.org/api-guide/pagination/
	'PAGE_SIZE': 10,
	'DEFAULT_AUTHENTICATION_CLASSES': (
  	'rest_framework_simplejwt.authentication.JWTAuthentication', #A: con token
		'rest_framework.authentication.SessionAuthentication', #A: si te logueaste en la ui web
	)
}

#S: servicios graphql
GRAPHENE = {
	'SCHEMA': 'pa_charlas_app.views_graphql.schema',
	'ATOMIC_MUTATIONS': True, #U: todos los cambios en un request o ninguno, #VER: https://docs.graphene-python.org/projects/django/en/latest/mutations/
	'MIDDLEWARE': [
		'pa_charlas_app.graphql_util.auth_middleware', #U: usar el mismo jwt que django rest
	],
	#VER: https://docs.graphene-python.org/projects/django/en/latest/introspection/
	#U: python manage.py graphql_schema
	'SCHEMA_OUTPUT': 'graphql_schema.json',  # defaults to schema.json,
	'SCHEMA_INDENT': 2,  # Defaults to None (displays all data on a single line)
}

#VER: https://github.com/adamchainz/django-cors-headers
CORS_URLS_REGEX = r'^/(api/.*|graphql/)$' #A: solo enviamos CORS allow para request a la api
CORS_ALLOW_ALL_ORIGINS= True #A:SEC: OjO! permitimos todos porque estamos filtrando con CORS_URLS_REGEX

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'UPDATE_LAST_LOGIN': False,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION', #VER: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html#auth-header-name
}
#A: para acceder con token hay que pasarlo en el header Authorization

if ES_HEROKU:
	django_heroku.settings(locals()) #A: Activate Django-Heroku.

