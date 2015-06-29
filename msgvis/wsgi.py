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
from mbcore import conf

project_root = path(__file__).abspath().realpath().dirname().parent
conf.configure(project_root, 'msgvis')
conf.load_env(default_settings_module="msgvis.settings.prod")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
