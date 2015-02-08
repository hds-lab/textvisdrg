#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    # Make sure the project root is on the path
    from path import path
    PROJECT_ROOT = path(__file__).abspath().realpath().dirname().parent
    sys.path.append(PROJECT_ROOT)

    # Load the .env file
    sys.path.append(PROJECT_ROOT / 'setup')
    from fabutils import env_file
    env_file.load(PROJECT_ROOT / '.env')

    # If that didn't set the settings module...
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msgvis.settings.prod")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
