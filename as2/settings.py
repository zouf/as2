## Django settings for nightout project.

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
import os.path
import socket
DEBUG = True

SPHINX_API_VERSION = 0x116
SPHINX_SERVER='127.0.0.1'




TEMPLATE_DEBUG = DEBUG
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', '..'))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
FIXTURE_DIRS = os.path.join(BASE_DIR, 'fixtures')


#Dataset locations
PREPOP_DIR = os.path.join(STATIC_ROOT, 'prepop')
DOH_DATASET_LOCATION = os.path.join(PREPOP_DIR, 'grades_raw.json')

#add your admin name heres
ADMINS = (
     ('Matt Zoufaly', 'matt@allsortz.com'),
)

DEV_BOXES = ['hydralisk', 'enceladus'] # add your dev computer here

#always use https
#SESSION_COOKIE_SECURE= True
#CSRF_COOKIE_SECURE = True
#CSRF_COOKIE_NAME = 'allsortz-cookie'
#CSRF_COOKIE_DOMAIN = 'allsortz.com' #your domain name


#for integration with facebook
FB_APP_SECRET = "586868267b93b17ed6c04e0a346018e5"
FB_APP_ID = "260788694033894"

#true if we're on the servers for deployment. In other words, any computer but
# the dev computers

if socket.gethostname() in DEV_BOXES:
    DEPLOY = False
else:
    DEPLOY = True
    


#paginator settings
ENDLESS_PAGINATION_PER_PAGE =5
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'admin@allsortz.com'
#EMAIL_HOST_PASSWORD = 'allsortz'
EMAIL_HOST_PASSWORD ='adminallsort'
EMAIL_PORT = 587


MANAGERS = ADMINS

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
#CELERY_IMPORTS = ("ratings.tasks", )
#CELERY_RESULT_BACKEND = "amqp"


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID='AKIAJNT6HH4SMZYBZJKQ'
AWS_SECRET_ACCESS_KEY='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'
AWS_STORAGE_BUCKET_NAME='allsortz-test'

#AWS_CALLING_FORMAT=CallingFormat.SUBDOMAIN

#the image links remain static
#uncomment to use default caching
AWS_QUERYSTRING_AUTH = False
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#import djcelery


#djcelery.setup_loader()


##old settings
if DEPLOY:
#use amazon RDS
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'allsortz_db',                      # Or path to database file if using sqlite3.
                # Not used with sqlite3.
            'USER': 'django',
            'PASSWORD': 'welcometoallsortz',                  # Not used with sqlite3.
#            'HOST': 'db.allsortz.com',
            'HOST': 'localhost',
            'PORT': '5432',       
                # Set to empty string for default. Not used with sqlite3.
        }
    }
    #FOR SPHINX
    DATABASE_ENGINE='postgresql'
    DATABASE_HOST='127.0.0.1'
    DATABASE_PORT='5432'
    DATABASE_USER='django'
    DATABASE_NAME='allsortz_db'
    DATABASE_PASSWORD='welcometoallsortz'
    #for amazon RDS
    #'USER': 'zouf',                  
    # 'HOST': 'rateoutdb-mysql.carvpvtur6or.us-east-1.rds.amazonaws.com',                      # Set to empty string for localhost. Not used with sqlite3.
    # 'PORT': '3306',      
else:
    DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'allsortz_db',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'zoufzouf',                  # Not used with sqlite3.
        'HOST': 'db.allsortz.com',
        'PORT': '5432',     
        }   
    }
    #FOR SPHINX
    DATABASE_ENGINE='postgresql'
    DATABASE_HOST='127.0.0.1'
    DATABASE_PORT='5432'
    DATABASE_USER='django'
    DATABASE_NAME='allsortz_db'
    DATABASE_PASSWORD='welcometoallsortz'
    
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1



# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"


#dont use AWS for debug


LOG_BASE = os.path.abspath(os.path.join('/var', 'log', 'as2'))
# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"

if not DEPLOY:
    STATIC_URL='/static/'
else:
    STATIC_URL='http://allsortz.s3-website-us-east-1.amazonaws.com/'
    
RESULTS_DIR = '/tmp/'
CLIB_DIR = os.path.join(BASE_DIR, 'clib')

PYTHON_PATH = os.path.join(BASE_DIR, 'clib')


STATIC_MEDIA_PATH=BASE_DIR+'/wiki/media/'
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	  ("css", BASE_DIR+ "/css"),
	  ("js", BASE_DIR+ "/js")
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v%m(kt379ic)zf+2p@6vn(ke6!@t=l$$%b)u5=3z0^q@psbh04'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS += (
     'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'api.middle_profile.ProfilerMiddleware',
#    'privatebeta.middleware.PrivateBetaMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

APPEND_SLASH = True
 

ROOT_URLCONF = 'as2.urls'

# URL of the login page.
LOGIN_URL = '/accounts/login/'


#haystack search plugin
#HAYSTACK_CONNECTIONS = {
#    'default': {
#        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
#        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
#    },
#}


# Python dotted path to the WSGI application used by Django's runserver.
#WSGI_APPLICATION = 'rateout.wsgi.application'

TEMPLATE_DIRS = (
	BASE_DIR+'/src/templates/',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'djangosphinx',
    'recommendation',
  	'registration', 
	 #'celery',
     #'djcelery',
    'storages',
    'queries',
    'wiki',
    'django.contrib.admin',
	'django.contrib.contenttypes',
    'django.contrib.gis',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

ACCOUNT_ACTIVATION_DAYS = 7

#import logging
#logging.basicConfig(
#	level=logging.DEBUG,
#	format='%(asctime)s %(levelname)s %(message)s',
#	filename='/tmp/django.log',
#	filemode='w'
#)



# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': LOG_BASE+'/mylog.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },  
        'allsortz_handler': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': LOG_BASE+'/allsortz_ratings.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'standard',
        },
        'request_handler': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': LOG_BASE+'/django_request.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'standard',
        },
         'send_email': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
                 
        'db_logging': {
            'level' : 'DEBUG',
            'class' : 'logging.handlers.RotatingFileHandler',
            'backupCount' : 5,
            'maxBytes': 1024*1024*5, # 5 MB,
            'filename':  LOG_BASE+'/django-db.log'
            },
    },
    'loggers': {
#        'ratings':{
#             'handlers': ['allsortz_handler', 'send_email'], #sends email on errors
#            'level': 'DEBUG',
#            'propagate': True      
#            },
        'django.db' : {
            'handlers' : ['db_logging'],
            'level' : 'DEBUG',
            'propagate': False,
            },
        '': {
            'handlers': ['allsortz_handler', 'send_email'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': { # Stop SQL debug from logging to main logger
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        
    }
}


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)
