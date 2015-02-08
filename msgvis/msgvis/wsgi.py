"""
WSGI config for msgvis project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys

from path import path
PROJECT_ROOT = path(__file__).abspath().realpath().dirname().parent.parent
sys.path.append(PROJECT_ROOT / 'setup')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msgvis.settings.prod")
from fabutils import env_file
env_file.load(PROJECT_ROOT / '.env')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
