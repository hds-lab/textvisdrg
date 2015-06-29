from msgvis.settings.common import *

DEV = False

DEBUG_TEMPLATE = DEBUG

COMPRESS_ENABLED = get_env_setting('COMPRESS_ENABLED', True, type=bool)
COMPRESS_OFFLINE = get_env_setting('COMPRESS_OFFLINE', True, type=bool)

ALLOWED_HOSTS = get_env_setting("ALLOWED_HOSTS", 'localhost').split(',')

# Supervisord settings
INSTALLED_APPS += (
    'djsupervisor',
)

SUPERVISOR_LOG_MAXBYTES = '50MB'
SUPERVISOR_LOG_BACKUPS = 10
WSGI_MODULE = 'msgvis.wsgi'
GUNICORN_CONF = PROJECT_ROOT / 'gunicorn.conf.py'
SUPERVISOR_PIDFILE = LOGS_ROOT / 'supervisord.pid'
# End supervisord settings

if 'debug_toolbar' in INSTALLED_APPS:
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    MIDDLEWARE_CLASSES = (
                             'debug_toolbar.middleware.DebugToolbarMiddleware',
                         ) + MIDDLEWARE_CLASSES
