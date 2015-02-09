"""
Django settings for msgvis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import sys
import os
from path import path
import dj_database_url

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting, default=None):
    """ Get the environment setting or return exception """
    if default is not None:
        return os.environ.get(setting, default)
    else:
        try:
            return os.environ[setting]
        except KeyError:
            error_msg = "Set the %s env variable" % setting
            raise ImproperlyConfigured(error_msg)

########## PATH CONFIGURATION
# Absolute filesystem path to the django site folder
SITE_ROOT = path(__file__).abspath().realpath().dirname().parent

# Absolute path to the top-level project folder
PROJECT_ROOT = SITE_ROOT.parent

# Site name:
SITE_NAME = SITE_ROOT.basename()

# Id for the Sites framework
SITE_ID = 1

########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = False
########## END DEBUG CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///%s' % (PROJECT_ROOT / 'development.sqlite'))
}
########## END DATABASE CONFIGURATION



########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-LOGIN_REDIRECT_URL
LOGIN_REDIRECT_URL = "/"
########## END GENERAL CONFIGURATION



########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = (SITE_ROOT / 'media').normpath()

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION




########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = get_env_setting('STATIC_ROOT', (SITE_ROOT / 'assets').normpath())
if not isinstance(STATIC_ROOT, path):
    STATIC_ROOT = path(STATIC_ROOT)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    (SITE_ROOT / 'static').normpath(),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
########## END STATIC FILE CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    (SITE_ROOT / 'fixtures').normpath(),
)
########## END FIXTURE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('SECRET_KEY', 'secret')
########## END SECRET CONFIGURATION

########## TEST CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
########## END TEST CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.core.context_processors.csrf',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'msgvis.base.context_processors.google_analytics',
)


# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    (SITE_ROOT / 'templates').normpath(),
)
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION



########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Utilities
    'django_extensions',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'msgvis.base',
    'msgvis.api',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGS_ROOT = get_env_setting('LOGS_ROOT', PROJECT_ROOT / 'logs')
if not isinstance(LOGS_ROOT, path):
    LOGS_ROOT = path(LOGS_ROOT)
if not LOGS_ROOT.exists():
    LOGS_ROOT.mkdir()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
########## END WSGI CONFIGURATION


########## TOOLBAR CONFIGURATION
# See: http://south.readthedocs.org/en/latest/installation.html#configuring-your-django-installation
INSTALLED_APPS += (
    # Database migration helpers:
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Only show the debug toolbar to users with the superuser flag.
def custom_show_toolbar(request):
    return request.user.is_superuser


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': '%s.settings.common.custom_show_toolbar' % SITE_NAME,
    'HIDE_DJANGO_SQL': True,
    'TAG': 'body',
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True,
}

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION


########## COMPRESSOR CONFIGURATION
# See: http://django-compressor.readthedocs.org/en/latest/quickstart/
INSTALLED_APPS += (
    'compressor',
)


def find_node_bin(package_name='less', bin_name='lessc'):
    p = PROJECT_ROOT / 'node_modules' / '.bin' / bin_name
    if p.exists():
        return p
    p = PROJECT_ROOT / 'node_modules' / package_name / 'bin' / bin_name
    if p.exists():
        return "node %s" % p
    return bin_name  # global install


BIN_COFFEE = find_node_bin('coffee-script', 'coffee')
BIN_COFFEE_COMMAND = '%s --compile --stdio' % BIN_COFFEE

BIN_LESSC = find_node_bin('less', 'lessc')
# The relative-urls flag is necessary since we are moving less files around.
BIN_LESSC_COMMAND = '%s --relative-urls {infile} {outfile}' % BIN_LESSC

COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', BIN_COFFEE_COMMAND),

    # this adds the CssAbsoluteFilter to the less filter
    ('text/less', BIN_LESSC_COMMAND),
)

COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OUTPUT_DIR = 'CACHE'
########## END COMPRESSOR CONFIGURATION


######### REST FRAMEWORK
INSTALLED_APPS += (
    'rest_framework',
)

REST_FRAMEWORK = {
}
######### END REST FRAMEWORK


######### ANGULAR JS CONFIG
INSTALLED_APPS += (
    'djangular',
)

######### END ANGULAR CONFIG
