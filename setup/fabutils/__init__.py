import sys
from path import path

def _wrap_path(possible_path):
    if not isinstance(possible_path, path):
        possible_path = path(possible_path)
    return possible_path

class Configuration(object):

    def __init__(self):
        self.PROJECT_ROOT = None
        self.DJANGO_PROJECT_NAME = None
        self.SITE_ROOT = None

    def is_configured(self):
        return self.PROJECT_ROOT is not None

    def configure(self, project_root, django_project_name):
        """
        project_root is a path to the top level project folder.
        django_project_name is the name of the folder where manage.py lives.
        """
        if self.is_configured():
            return

        self.PROJECT_ROOT = _wrap_path(project_root)
        self.SITE_ROOT = self.PROJECT_ROOT / django_project_name
        self.DJANGO_PROJECT_NAME = django_project_name

        sys.path.append(self.PROJECT_ROOT)

conf = Configuration()
