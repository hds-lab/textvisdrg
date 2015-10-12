"""
Define common admin and maintenance tasks here.
For more info: http://docs.fabfile.org/en/latest/
"""

import sys

from path import path
from fabric.api import run, env, prefix, quiet, abort


PROJECT_ROOT = path(__file__).abspath().realpath().dirname()
sys.path.append(PROJECT_ROOT / 'setup')

from fabutils import conf

conf.configure(PROJECT_ROOT, 'msgvis')

from fabutils import factories
from fabutils.tasks import *

pip_requirements = {
    'dev': ('-r requirements/dev.txt',),
    'prod': ('-r requirements/prod.txt',),
    'test': ('-r requirements/test.txt',),
}

required_nltk_corpora = ["stopwords", "punkt", "wordnet"]

pip_install = factories.pip_install_task(pip_requirements, default_env='dev')

def dependencies(default_env='dev'):
    """Install requirements for pip, npm, and bower all at once."""
    pip_install(default_env)
    npm_install()
    bower_install()
    nltk_init()

test = factories.test_task(default_settings='msgvis.settings.test')
test_coverage = factories.coverage_task(default_settings='msgvis.settings.test')

test_data_path = conf.PROJECT_ROOT / 'setup' / 'fixtures' / 'test_data.json'
make_test_data = factories.make_test_data_task(('base', 'api',  # 'corpus',
                                                'dimensions', 'datatable',
                                                'importer', 'enhance', 'questions',
                                                'auth', '--exclude=auth.Permission'),
                                               test_data_path)
load_test_data = factories.load_test_data_task(test_data_path)


# Model keys to fixture paths from PROJECT_ROOT
model_fixtures = (
    ('corpus.Language', 'msgvis/apps/corpus/fixtures/languages.json'),
    ('corpus.MessageType', 'msgvis/apps/corpus/fixtures/messagetypes.json'),
    ('corpus.Timezone', 'msgvis/apps/corpus/fixtures/timezones.json'),
    ('dimensions', 'msgvis/apps/dimensions/fixtures/dimensions.json'),
    ('questions', 'msgvis/apps/questions/fixtures/questions.json'),
)

def generate_fixtures():
    """
    Regenerate configured fixtures from the database.
    """
    generated = []
    for model, fixturefile in model_fixtures:
        fabutils.manage_py('dumpdata --indent=2 {model} > {out}'.format(
            model=model,
            out=PROJECT_ROOT / fixturefile,
        ))
        generated.append(fixturefile)

    print "Generated %d fixtures:" % len(generated)
    if len(generated) > 0:
        print " - " + '\n - '.join(generated)


def load_fixtures():
    """
    Replaces the database tables with the contents of fixtures.
    """
    for model, fixturefile in model_fixtures:
        fabutils.manage_py('syncdata %s' % (PROJECT_ROOT / fixturefile,))


def import_corpus(dataset_file_or_dir):
    """Import a dataset from a file"""
    dataset_file_or_dir = path(dataset_file_or_dir).abspath().realpath()
    fabutils.manage_py('import_corpus %s' % dataset_file_or_dir)


def restart_webserver():
    """Restart a local gunicorn process"""
    print green("Restarting gunicorn...")
    fabutils.manage_py('supervisor restart webserver')


def supervisor():
    """Starts the supervisor process"""
    print green("Supervisor launching...")
    fabutils.manage_py('supervisor')


def deploy(branch=None):
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
        run('which python')
        
        # Check prereqs
        with quiet():
            pips = run('pip freeze')
        if "Fabric" not in pips or 'path.py' not in pips:
            print green("Installing Fabric...")
            run('pip install -q Fabric path.py')

        run('git pull')
        if branch:
            run('git checkout %s' % branch)
            run('git pull')

        run('fab dependencies:prod')
        run('fab print_env check_database migrate')
        run('fab build_static restart_webserver')


def topic_pipeline(dataset, name="my topic model", num_topics=30):
    """Run the topic pipeline on a dataset"""
    command = "extract_topics --topics %d --name '%s' %s" % (int(num_topics), name, dataset)
    fabutils.manage_py(command)


def info():
    """Print a bunch of info about the environment"""
    fabutils.env_info()

    print os.linesep, green("---------- Scientific computing packages ------------"), os.linesep
    fabutils.try_load_module('nltk')
    fabutils.try_load_module('gensim')

    numpy = fabutils.try_load_module('numpy')
    if numpy is not None:

        print "  Numpy sysinfo:"
        import numpy.distutils.system_info as sysinfo

        print "   lapack:", sysinfo.get_info('lapack')
        print "     blas:", sysinfo.get_info('blas')
        print "    atlas:", sysinfo.get_info('atlas')


nltk_init = factories.nltk_download_task(required_nltk_corpora)


def memcached_status():
    """Display the status of the memcached server"""
    denv = fabutils.dot_env(default={})
    if denv.get('MEMCACHED_LOCATION', None) is not None:
        local("watch -n1 -d 'memcstat --servers %s'" % denv.get('MEMCACHED_LOCATION', None))
    else:
        print yellow("Set MEMCACHED_LOCATION in .env")
