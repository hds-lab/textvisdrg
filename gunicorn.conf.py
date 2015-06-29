# Configuration for gunicorn

import os, sys
from path import path
from mbcore import conf

project_root = path(__file__).abspath().realpath().dirname()
conf.configure(project_root, 'msgvis')
conf.load_env(default_settings_module="msgvis.settings.prod")

bind = "%(ip)s:%(port)s" % {
    'port': os.environ.get('PORT', '8000'),
    'ip': os.environ.get('SERVER_HOST', '127.0.0.1')
}

from django.conf import settings
workers = os.environ.get("GUNICORN_WORKERS", 1)

accesslog = settings.LOGS_ROOT / 'gunicorn.access.log'
errorlog = settings.LOGS_ROOT / 'gunicorn.error.log'

timeout = int(os.environ.get("GUNICORN_TIMEOUT", 30))

if settings.DEBUG:
    loglevel = 'debug'
