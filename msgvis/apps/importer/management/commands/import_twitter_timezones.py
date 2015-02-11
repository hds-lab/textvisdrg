from django.core.management.base import BaseCommand, make_option

from msgvis.apps.importer import twitter
from msgvis.apps.corpus import models as corpus_models


class Command(BaseCommand):
    """
    Obtains a mapping of the Twitter-supported timezones from the Ruby on Rails TimeZone class.

    .. note::

        Requires `Ruby on Rails <http://rubyonrails.org/download/>`_ to be installed: ``gem install rails``.

    Example:

    .. code-block :: bash

        $ python manage.py import_twitter_timezones

    """
    help = "Import Twitter-supported timezones from the Ruby on Rails TimeZone class."

    def handle(self, *args, **options):

        if twitter.ror_installed():

            # Get languages from Twitter
            timezones = twitter.get_timezones()

        else:
            raise Exception("Ruby on Rails not installed! Run 'gem install rails'.")
