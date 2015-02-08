from msgvis.settings.common import *

DEV = False

DEBUG = bool(get_env_setting('DEBUG', False))
DEBUG_TEMPLATE = DEBUG

COMPRESS_ENABLED = bool(get_env_setting('COMPRESS_ENABLED', True))
COMPRESS_OFFLINE = bool(get_env_setting('COMPRESS_OFFLINE', True))

ALLOWED_HOSTS = get_env_setting("ALLOWED_HOSTS", 'localhost').split(',')

# Supervisord settings
INSTALLED_APPS += (
    'djsupervisor',
)

SUPERVISOR_LOG_MAXBYTES = '50MB'
SUPERVISOR_LOG_BACKUPS = 10
WSGI_MODULE = 'msgvis.wsgi'
GUNICORN_CONF = PROJECT_ROOT / 'gunicorn.conf.py'
# End supervisord settings
