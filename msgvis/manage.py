#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    from path import path
    PROJECT_ROOT = path(__file__).abspath().realpath().dirname().parent
    sys.path.append(PROJECT_ROOT / 'setup')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msgvis.settings.prod")
    from fabutils import env_file
    env_file.load(PROJECT_ROOT / '.env')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
