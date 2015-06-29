#!/usr/bin/env python
import sys

if __name__ == "__main__":

    # Make sure the project root is on the path
    from path import path
    from mbcore import conf

    project_root = path(__file__).abspath().realpath().dirname().parent
    conf.configure(project_root, 'msgvis')
    conf.load_env(default_settings_module="msgvis.settings.prod")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
