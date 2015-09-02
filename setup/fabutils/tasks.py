"""
A collection of runnable fabric tasks.
Make sure to call conf.configure() first!
"""
from path import path
from fabric.api import local, lcd, abort
from fabric.colors import green, yellow, red
import os

from fabutils import conf, utils as fabutils


def pull():
    """Just runs git pull"""

    print green("Pulling latest code...")
    local('git pull')
    print "Git pull successful."


def manage(command):
    """Run a Django management command."""
    fabutils.manage_py(command)


def migrate():
    """Runs migrations"""

    print green("Running migrations...")
    if fabutils.manage_py('migrate'):
        print "Migrations successful."


def build_static():
    """Builds static files for production"""

    print green("Gathering and preprocessing static files...")
    fabutils.manage_py('collectstatic --noinput -i media')
    fabutils.manage_py('compress')


def docs(easy=None):
    """Build the documentation"""

    docs_dir = conf.PROJECT_ROOT / 'docs'
    if docs_dir.exists() and (docs_dir / 'Makefile').exists():
        print green("Rebuilding the Sphinx documentation...")
        with lcd(docs_dir):
            if easy is not None:
                local('make clean html')
            else:
                local('make clean html SPHINXOPTS="-n -W -T"')
    else:
        print yellow("No Sphinx documentation to build.")


def runserver():
    """Runs the Django development server"""

    print green("Running the development webserver...")
    denv = fabutils.dot_env()
    host = denv.get('SERVER_HOST', '0.0.0.0')
    port = denv.get('PORT', '8000')
    fabutils.manage_py('runserver %s:%s' % (host, port))


def reset_db():
    """Removes all of the tables"""
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

def interpolate_env(outpath=None):
    """Writes a .env file with variables interpolated from the current environment"""

    if outpath is None:
        outpath = conf.PROJECT_ROOT / '.env'
    else:
        outpath = path(outpath)

    dot_env_path = conf.PROJECT_ROOT / 'setup' / 'templates' / 'dot_env'

    fabutils.django_render(dot_env_path, outpath, os.environ)

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


def npm_install():
    """Install npm requirements"""
    print green("Updating npm dependencies...")

    if fabutils.npm_install():
        print "Npm dependency update successful."
    else:
        abort(red("Npm dependency update failed."))

def bower_install():
    """Install bower requirements"""
    print green("Updating bower dependencies...")

    if fabutils.bower_install():
        print "Bower dependency update successful."
    else:
        abort(red("Bower dependency update failed."))
