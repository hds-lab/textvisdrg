"""
Define common admin and maintenance tasks here.
For more info: http://docs.fabfile.org/en/latest/
"""

import sys

from path import path
from fabric.api import run, env, prefix, quiet


PROJECT_ROOT = path(__file__).abspath().realpath().dirname()
sys.path.append(PROJECT_ROOT / 'setup')

from fabutils import conf

conf.configure(PROJECT_ROOT, 'msgvis')

from fabutils import factories
from fabutils.tasks import *

# A dependencies management task
dependencies = factories.dependencies_task(
    {
        'dev': ('-r requirements/dev.txt',),
        'prod': ('-r requirements/prod.txt',),
        'test': ('-r requirements/test.txt',),
    },
    default_env='dev'
)

test = factories.test_task(default_settings='msgvis.settings.test')
test_coverage = factories.coverage_task(default_settings='msgvis.settings.test')

test_data_path = conf.PROJECT_ROOT / 'setup' / 'fixtures' / 'test_data.json'
make_test_data = factories.make_test_data_task(('base', 'api', #'corpus',
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
        run('fab dependencies:prod')
        run('fab print_env check_database migrate')
        run('fab build_static restart_webserver')

_django_set_up = False
def _setup_django(debug=None):
    global _django_set_up

    if not _django_set_up:

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "msgvis.settings.dev")

        from msgvis import env_file
        env_file.load()

        if debug is not None:
            os.environ.setdefault("DEBUG", str(debug))

        import django
        django.setup()

        _django_set_up = True

def _data_pipeline(context, num_topics):
    dictionary = context.find_dictionary()
    if dictionary is None:
        dictionary = context.build_dictionary()

    if not context.bows_exist(dictionary):
        context.build_bows(dictionary)

    model, lda = context.build_lda(dictionary, num_topics=num_topics)
    context.apply_lda(dictionary, model, lda)
    context.evaluate_lda(dictionary, model, lda)

def tweet_pipeline(name="tweet data, no punctuation", num_topics=30):
    import logging
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, )

    _setup_django(debug=False)

    from msgvis.apps.enhance.tasks import get_twitter_context
    context = get_twitter_context(name)
    _data_pipeline(context, num_topics=int(num_topics))