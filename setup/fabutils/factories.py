"""Functions for making fab tasks"""

from fabric.api import local, abort
from fabric.colors import green, red, yellow
from fabutils import utils as fabutils, conf


def dependencies_task(pip_requirements, pip=False, npm=False, bower=False, default_env='dev'):
    """
    Build a task for installing dependencies.

    ``pip_requirements`` should be a dict mapping environment keys to pip settings.
    """

    def dependencies(environment=default_env):
        """Installs Python, NPM, and Bower packages"""

        print green("Updating %s dependencies..." % environment)

        reqs = pip_requirements[environment]

        success = True
        if success and pip:
            success = success and fabutils.pip_install(reqs)
        if success and npm:
            success = success and fabutils.npm_install()
        if success and bower:
            success = success and fabutils.bower_install()

        if success:
            print "Dependency update successful."
        else:
            abort(red("Dependency update failed."))

    return dependencies


def test_task(default_settings):
    def test(settings_module=default_settings):
        """Run tests"""
        fabutils.django_tests(settings_module, coverage=False)

    return test


def coverage_task(default_settings):
    def test_coverage(settings_module=default_settings):
        """Run tests with coverage"""
        fabutils.django_tests(settings_module, coverage=True)

    return test_coverage


def make_test_data_task(test_data_apps, default_test_data_path):
    def make_test_data(outfile=None):
        """Updates the test_data.json file based on what is in the database"""

        if outfile is None:
            outfile = default_test_data_path

        print green("Saving test data from %s to %s" % (test_data_apps, outfile))
        args = ' '.join(test_data_apps + ('--exclude=auth.Permission',))
        if fabutils.manage_py("dumpdata --indent=2 %s > %s" % (args, outfile)):
            print "Make test data successful."

    return make_test_data

def load_test_data_task(default_test_data_path):
    def load_test_data(infile=None):
        """Load test data from test_data.json"""

        if infile is None:
            infile = default_test_data_path

        if infile.exists():
            print green("Loading test data from %s" % infile)
            if fabutils.manage_py("loaddata %s" % infile):
                print "Load test data successful."
        else:
            print yellow("No test data found")

    return load_test_data
