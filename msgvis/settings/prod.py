from msgvis.settings.common import *

DEV = False

DEBUG = bool(get_env_setting('DEBUG', False))
DEBUG_TEMPLATE = DEBUG

COMPRESS_ENABLED = bool(get_env_setting('COMPRESS_ENABLED', True))
COMPRESS_OFFLINE = bool(get_env_setting('COMPRESS_OFFLINE', True))


ALLOWED_HOSTS = ('127.0.0.1','localhost',)

print DEBUG
