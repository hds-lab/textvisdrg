"""
Define common admin and maintenance tasks here.
For more info: http://docs.fabfile.org/en/latest/
"""

django_project_name = 'msgvis'
pip_requirements = ('-r requirements/dev.txt',)
test_data_apps = ('msgvis',)

import sys
import os
from path import path
from fabric.api import local, run, env, prefix, quiet
from fabric.colors import red, green, yellow
from fabric.operations import prompt

PROJECT_ROOT = path(__file__).abspath().realpath().dirname()
sys.path.append(PROJECT_ROOT / 'setup')
from fabutils import utils as fabutils

fabutils.configure(PROJECT_ROOT, django_project_name)


def dependencies():
    """Installs Python, NPM, and Bower packages"""

    print green("Updating dependencies...")
    if fabutils.pip_install(pip_requirements) and \
        fabutils.npm_install() and \
        fabutils.bower_install():
        print "Dependency update successful."


def migrate():
    """Runs migrations"""

    print green("Running migrations...")
    if fabutils.manage_py('migrate'):
        print "Migrations successful."


def build_static():
    """Builds static files for production"""

    print green("Gathering and preprocessing static files...")
    fabutils.manage_py('collectstatic --noinput')
    fabutils.manage_py('compress')


def runserver():
    """Runs the Django development server"""

    print green("Running the development webserver...")
    denv = fabutils.dot_env()
    host = denv.get('SERVER_HOST', '0.0.0.0')
    port = denv.get('PORT', '8000')
    fabutils.manage_py('runserver %s:%s' % (host, port))


def load_test_data():
    """Load test data from test_data.json"""

    infile = PROJECT_ROOT / 'setup' / 'fixtures' / 'test_data.json'

    if infile.exists():
        print green("Loading test data from %s" % infile)
        if fabutils.manage_py("loaddata %s" % infile):
            print "Load test data successful."
    else:
        print yellow("No test data found")


def make_test_data():
    """Updates the test_data.json file based on what is in the database"""

    outfile = PROJECT_ROOT / 'setup' / 'fixtures' / 'test_data.json'

    print green("Saving test data from %s to %s" % (test_data_apps, outfile))
    args = ' '.join(test_data_apps + ('--exclude=auth.Permission',))
    if fabutils.manage_py("dumpdata --indent=2 %s > %s" % (args, outfile)):
        print "Make test data successful."


def reset_db():
    """Removes all of the tables"""

    settings = fabutils.django_settings()
    denv = fabutils.dot_env()
    print denv
    print red("WARNING! Deleting the database! (%s)" % settings.DATABASES['default']['NAME'])

    fabutils.manage_py("reset_db")


def clear_cache():
    """Deletes the cached static files"""

    settings = fabutils.django_settings()

    if hasattr(settings, 'COMPRESS_ROOT'):
        cache_dir = settings.COMPRESS_ROOT / settings.COMPRESS_OUTPUT_DIR

        # a safety check
        if cache_dir.exists() and cache_dir.endswith("CACHE"):
            print green("Removing %s" % cache_dir)
            cache_dir.rmdir_p()
            print "Clear cache successful."
    else:
        print yellow("Django not configured for static file compression")


def pull():
    """Just runs git pull"""

    print green("Pulling latest code...")
    local('git pull')
    print "Git pull successful."


def reset_dev(pull=None):
    """
    Fully update the development environment.
    This is useful after a major update.

    Runs reset_db, [git pulls], installs dependencies, migrate, load_test_data, and clear_cache.
    """
    print "\n"
    reset_db()

    if pull is not None:
        print "\n"
        pull()

    print "\n"
    dependencies()

    print "\n"
    migrate()

    print "\n"
    load_test_data()

    print "\n"
    clear_cache()


def interpolate_env(outpath=None):
    """Writes a .env file with variables interpolated from the current environment"""

    if outpath is None:
        outpath = PROJECT_ROOT / '.env'
    else:
        outpath = path(outpath)

    dot_env_path = PROJECT_ROOT / 'setup' / 'templates' / 'dot_env'

    fabutils.django_render(dot_env_path, outpath, os.environ)


def gunicorn_restart():
    """Restart a local gunicorn process"""


def check_database():
    """Makes sure the database is accessible"""

    if fabutils.test_database():
        print green("Database is available")
    else:
        settings = fabutils.django_settings()
        print red("Database is not available! (%s)" % settings.DATABASES['default']['NAME'])


def print_env():
    """Print the local .env file contents"""
    denv = fabutils.dot_env()
    import pprint
    pprint.pprint(denv)


def deploy():
    """
    SSH into a remote server, run commands to update deployment,
    and start the server.
    
    This requires that the server is already running a 
    fairly recent copy of the code.

    Furthermore, the app must use a
    """

    denv = fabutils.dot_env()

    host = denv.get('DEPLOY_HOST', None)
    virtualenv = denv.get('DEPLOY_VIRTUALENV', None)

    if host is None:
        print red("No DEPLOY_HOST in .env file")
        return
    if virtualenv is None:
        print red("No DEPLOY_VIRTUALENV in .env file")
        return

    env.host_string = host

    with prefix('workon %s' % virtualenv):

        # Check prereqs
        with quiet():
            pips = run('pip freeze')
            if "Fabric" not in pips or 'path.py' not in pips:
                print green("Installing Fabric...")
                run('pip install Fabric path.py')

        run('fab pull')
        run('fab dependencies')
        run('fab print_env check_database migrate')
        run('fab build_static gunicorn_restart')

