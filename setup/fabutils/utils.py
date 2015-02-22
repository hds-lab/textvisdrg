import sys
import os
from path import path

from fabric.context_managers import warn_only, quiet, prefix, hide
from fabric.api import env, local, lcd
from fabric.colors import red, yellow, green

from fabutils import conf, _wrap_path



_env_already_read = None
_package_already_read = None
_django_settings = None
_django_project_module = None




def require_configured(fn):
    def real_fn(*args, **kwargs):
        if not conf.is_configured():
            raise Exception("Call configure() first.")
        return fn(*args, **kwargs)

    return real_fn


@require_configured
def django_module():
    import importlib

    global _django_project_module
    _django_project_module = importlib.import_module(conf.DJANGO_PROJECT_NAME)


@require_configured
def dot_env(default=None):
    """Parse the .env file and return a dictionary"""

    global _env_already_read

    if not _env_already_read:
        from fabutils import env_file

        _env_already_read = env_file.read(conf.PROJECT_ROOT / '.env', default=default)

    return _env_already_read


@require_configured
def package_json():
    """Parse the package.json file"""

    global _package_already_read

    if not _package_already_read:
        import json

        with open(conf.PROJECT_ROOT / 'package.json') as packfile:
            _package_already_read = json.load(packfile)

    return _package_already_read


@require_configured
def django_settings(default_settings_module='settings'):
    """Return the django settings object."""

    denv = dot_env()

    env.django_settings_module = denv.get('DJANGO_SETTINGS_MODULE', default_settings_module)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', env.django_settings_module)

    from django.conf import settings

    import django
    django.setup()

    return settings


def symlink_supported():
    """Return True if the system can sustain symlinks."""
    with quiet():
        result = local('ln -s __linktest__target __linktest__source').succeeded
        local('rm -f __linktest__source __linktest__target')
        return result


@require_configured
def manage_py(args):
    """Run a manage.py task"""

    with lcd(conf.SITE_ROOT):
        if (conf.SITE_ROOT / 'manage.py').exists():
            local('python manage.py %s' % args)
            return True
        else:
            print yellow("Django script manage.py doesn't exist in %s" % conf.SITE_ROOT)
            return False


def _django_test_command(settings_module):
    """Get the manage.py test command for Django"""
    manage_script = conf.SITE_ROOT / 'manage.py'
    if not manage_script.exists():
        print yellow("Django script manage.py doesn't exist in %s" % conf.SITE_ROOT)
        return None

    return '{MANAGE_PY} test --settings={SETTINGS}'.format(
        MANAGE_PY=manage_script,
        SETTINGS=settings_module
    )


def django_tests(settings_module, coverage=False):
    """Run django tests, optionally with coverage."""

    test_cmd = _django_test_command(settings_module)
    if test_cmd is None:
        return False

    # Tests require a .env file
    ensure_test_env()

    if coverage:
        test_cmd = 'coverage run --source={SOURCE} {TEST_CMD} && coverage report'.format(
            SOURCE=conf.SITE_ROOT,
            TEST_CMD=test_cmd
        )

    with lcd(conf.PROJECT_ROOT):
        local(test_cmd)
        return True


@require_configured
def pip_install(requirements):
    """Install some pip requirements"""

    if isinstance(requirements, basestring):
        requirements = (requirements,)

    pip_path = path(local('which pip', capture=True))
    if not pip_path.exists():
        print pip_path
        print red("Cannot find pip!")
        return False

    use_sudo = False
    if pip_path.get_owner() == 'root':
        # If pip is owned by root, we are gonna need sudo
        use_sudo = True

    print "Installing python requirements..."

    with lcd(conf.PROJECT_ROOT):

        for req in requirements:
            if use_sudo:
                result = local('sudo pip install -q %s' % req)
            else:
                result = local('pip install -q %s' % req)

            if not result.succeeded:
                print red("Failed to install %s" % req)
                return False

    return True


@require_configured
def npm_install():
    """Install npm modules"""

    print "Installing npm modules..."

    with lcd(conf.PROJECT_ROOT):
        if path(conf.PROJECT_ROOT / 'package.json').exists():
            if symlink_supported():
                local('npm install')
            else:
                print yellow("Symbolic links not supported. Using no-bin-link option.")
                local('npm install --no-bin-link')

            return True

        else:
            print yellow("Node.js package.json doesn't exist")
            return False


@require_configured
def bower_install():
    """Install bower packages"""
    print "Installing bower packages..."

    with lcd(conf.PROJECT_ROOT):
        if path(conf.PROJECT_ROOT / 'bower.json').exists():
            print "Installing bower requirements..."
            local('bower prune --config.interactive=false')
            local('bower install --config.interactive=false')

            return True
        else:
            print yellow("File bower.json doesn't exist")
            return False


@require_configured
def django_render(template_file, output_file, context):
    """Use the Django template engine to render a template with a context dict"""
    from django.template import Template, Context

    from django.conf import settings

    if not settings.configured:
        settings.configure()

    output_file = _wrap_path(output_file)
    template_file = _wrap_path(template_file)

    if output_file.exists():
        local('mv %s %s.bak' % (output_file, output_file))
        print "Backed up %s file as %s.bak" % (output_file, output_file)

    with open(template_file, 'rb') as infile:
        template = Template(infile.read())

        with open(output_file, 'wb') as outfile:
            outfile.write(template.render(Context(context)))


@require_configured
def test_database():
    """Return true if the database is accessible."""
    django_settings()
    from django import db

    try:
        db.connection.cursor()
        return True
    except db.OperationalError:
        return False

@require_configured
def ensure_test_env(outpath=None):
    """Make an empty .env file for testing purposes."""
    if outpath is None:
        outpath = conf.PROJECT_ROOT / '.env'
    else:
        outpath = path(outpath)

    if not outpath.exists():
        # It's fine if it's empty, just make sure it exists
        local('touch %s' % outpath)

def try_load_module(module_name):
    """
    Import a module by name, print the version info and file name.
    Return None on failure.
    """
    try:
        import importlib
        mod = importlib.import_module(module_name)
        print green("%s %s:" % (module_name, mod.__version__)), mod.__file__
        return mod
    except ImportError:
        print yellow("Could not find nltk")
        return None

def env_info():
    """Print a ton of stuff about the environment"""
    from pprint import pprint
    import pip

    print green("---------- System info ------------")
    print os.linesep, "System OS:"
    local('uname -a && cat /etc/*-release')

    print os.linesep, green("---------- Project info ------------")
    print os.linesep, green("Project dir:")
    print "  ", conf.PROJECT_ROOT

    print os.linesep, green("Git branch:")
    local('git branch -v')

    print os.linesep, green("Last three commits:")
    local('git log -3')

    print os.linesep, green("---------- Python environment ------------")

    print os.linesep, "Python version: %s" % sys.version

    print os.linesep, green("Environment:")
    pprint(os.environ.data)

    print os.linesep, green("System Path:")
    pprint(sys.path)

    print os.linesep, green("Pip Distributions:")
    pprint(sorted(["%s==%s" % (i.key, i.version) for i in pip.get_installed_distributions()]))

    print os.linesep, green("---------- Deployment info ------------")

    print os.linesep, ".env file:"
    denv = dot_env(default={})
    pprint(denv)
