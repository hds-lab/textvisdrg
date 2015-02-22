"""Functions for making fab tasks"""

from fabric.api import local, abort
from fabric.colors import green, red, yellow
from fabutils import utils as fabutils, conf

def task_factory(fn):
    """Make a task look like it came from the fabfile. This tricks sphinx into documenting it."""
    def inner(*args, **kwargs):
        task = fn(*args, **kwargs)
        task.__module__ = 'fabfile'
        return task
    return inner

@task_factory
def pip_install_task(pip_requirements, default_env='dev'):
    """
    Build a task for installing pip dependencies.

    ``pip_requirements`` should be a dict mapping environment keys to pip settings.
    """

    def pip_install(environment=default_env):
        print green("Updating pip %s requirements..." % environment)

        reqs = pip_requirements[environment]

        if fabutils.pip_install(reqs):
            print green("Pip install update successful.")
        else:
            abort(red("Pip dependency update failed."))

    options = []
    for p in pip_requirements.keys():
        if p == default_env:
            p = "[%s]" % p
        options.append(p)
    pip_install.__doc__ = "Install pip requirements for an environment: %s" % ", ".join(options)

    return pip_install

@task_factory
def test_task(default_settings):

    def test(settings_module=default_settings):
        """Run tests"""
        fabutils.django_tests(settings_module, coverage=False)

    return test

@task_factory
def coverage_task(default_settings):

    def test_coverage(settings_module=default_settings):
        """Run tests with coverage"""
        fabutils.django_tests(settings_module, coverage=True)

    return test_coverage

@task_factory
def make_test_data_task(test_data_apps, default_test_data_path):

    def make_test_data(outfile=default_test_data_path):
        """Updates the test_data.json file based on what is in the database"""

        print green("Saving test data from %s to %s" % (test_data_apps, outfile))
        args = ' '.join(test_data_apps + ('--exclude=auth.Permission',))
        if fabutils.manage_py("dumpdata --indent=2 %s > %s" % (args, outfile)):
            print "Make test data successful."

    return make_test_data

@task_factory
def load_test_data_task(default_test_data_path):

    def load_test_data(infile=default_test_data_path):
        """Load test data from test_data.json"""
        if infile.exists():
            print green("Loading test data from %s" % infile)
            if fabutils.manage_py("loaddata %s" % infile):
                print "Load test data successful."
        else:
            print yellow("No test data found")

    return load_test_data

@task_factory
def nltk_download_task(required_nltk_corpora):
    def nltk_download():
        """Download required nltk corpora"""
        try:
            import nltk

            if not nltk.download(required_nltk_corpora):
                abort(red('Unable to download nltk corpora: %s' % required_nltk_corpora))
        except ImportError:
            abort(red("Failed to import nltk"))

    return nltk_download
