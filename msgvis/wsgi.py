"""
WSGI config for msgvis project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys

# Make sure the project root is on the path
from path import path
PROJECT_ROOT = path(__file__).abspath().realpath().dirname().parent
sys.path.append(PROJECT_ROOT)

# Load the .env file
sys.path.append(PROJECT_ROOT / 'setup')
from fabutils import env_file
env_file.load(PROJECT_ROOT / '.env')

# Just in case that didn't do it...
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msgvis.settings.prod")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
