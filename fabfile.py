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

required_nltk_corpora = ["stopwords", "punkt"]

# A dependencies management task
dependencies = factories.dependencies_task(pip_requirements,
                                           default_env='dev')

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
model_fixtures = {
    'corpus.Language': 'msgvis/apps/corpus/fixtures/languages.json',
    'corpus.MessageType': 'msgvis/apps/corpus/fixtures/messagetypes.json',
    'corpus.Timezone': 'msgvis/apps/corpus/fixtures/timezones.json',
}


def generate_fixtures(app_or_model=None):
    """
    Regenerate configured fixtures from the database.

    A Django app name or app model (app.Model) may be given as a parameter.
    """
    model_filter = None
    app_filter = None
    if app_or_model:
        if '.' in app_or_model:
            model_filter = app_or_model
        else:
            app_filter = '%s.' % app_or_model

    generated = []
    for model, fixturefile in model_fixtures.iteritems():
        if model_filter and model != model_filter:
            continue
        if app_filter and not model.startswith(app_filter):
            continue

        fabutils.manage_py('dumpdata --indent=2 {model} > {out}'.format(
            model=model,
            out=PROJECT_ROOT / fixturefile,
        ))
        generated.append(fixturefile)

    print "Generated %d fixtures:" % len(generated)
    if len(generated) > 0:
        print " - " + '\n - '.join(generated)


def load_fixtures(app_or_model=None):
    """
    Replaces the database tables with the contents of fixtures.

    A Django app name or app model (app.Model) may be given as a parameter.
    """

    model_filter = None
    app_filter = None
    if app_or_model:
        if '.' in app_or_model:
            model_filter = app_or_model
        else:
            app_filter = '%s.' % app_or_model

    for model, fixturefile in model_fixtures.iteritems():
        if model_filter and model != model_filter:
            continue
        if app_filter and not model.startswith(app_filter):
            continue
        fabutils.manage_py('syncdata %s' % (PROJECT_ROOT / fixturefile,))


def restart_webserver():
    """Restart a local gunicorn process"""
    print green("Restarting gunicorn...")
    fabutils.manage_py('supervisor restart webserver')


def supervisor():
    """Starts the supervisor process"""
    print green("Supervisor launching...")
    fabutils.manage_py('supervisor')

def dtest():
    denv = fabutils.dot_env()

    host = denv.get('DEPLOY_HOST', None)
    virtualenv = denv.get('DEPLOY_VIRTUALENV', None)
    env.host_string = host

    with prefix('workon %s' % virtualenv):
        has_bower = run('which bower')
        print has_bower

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
                run('pip install -q Fabric path.py')

        run('fab pull')
        run('fab dependencies:prod')
        run('fab print_env check_database migrate')
        run('fab build_static restart_webserver')


def topic_pipeline(dataset, name="my topic model", num_topics=30):
    command = "extract_topics --topics %d --name '%s' %s" % (num_topics, name, dataset)
    fabutils.manage_py(command)


def info():
    from pprint import pprint

    import pip
    import os, sys

    print green("---------- System info ------------")
    print "System OS:"
    local('uname -a && cat /etc/*-release')

    print "Project dir:"
    print "  ", PROJECT_ROOT

    print "Git branch:"
    local('git branch -v')

    print "Last three commits:"
    local('git log -3')

    print green("---------- Python environment ------------")

    print "Python version: %s" % sys.version

    print "Environment:"
    pprint(os.environ.data)

    print "System Path:"
    pprint(sys.path)

    print "Pip Distributions:"
    pprint(sorted(["%s==%s" % (i.key, i.version) for i in pip.get_installed_distributions()]))

    print green("---------- Checking specific packages ------------")
    try:
        import nltk

        print green("NLTK %s:" % nltk.__version__), nltk.__file__
    except ImportError:
        print yellow("Could not find nltk")

    try:
        import numpy

        print green("Numpy %s:" % numpy.__version__), numpy.__file__

        print "Numpy sysinfo:"
        import numpy.distutils.system_info as sysinfo

        sysinfo.get_info('lapack')
        sysinfo.get_info('blas')
        sysinfo.get_info('atlas')

    except ImportError:
        print yellow("Could not find numpy")

    try:
        import gensim

        print green("Gensim %s:" % gensim.__version__), gensim.__file__
    except ImportError:
        print yellow("Could not find gensim")


def nltk_init():
    try:
        import nltk

        if not nltk.download(required_nltk_corpora):
            abort(red('Unable to download nltk corpora: %s' % required_nltk_corpora))
    except ImportError:
        abort(red("Failed to import nltk"))
