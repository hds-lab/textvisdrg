from django.core.management.base import BaseCommand

from msgvis.apps.importer import twitter
from msgvis.apps.corpus import models as corpus_models


class Command(BaseCommand):
    """
    Import supported languages from the Twitter API into the database.
    If the languages already exist in the database, they will not be duplicated.

    .. note::

        Requires the `tweepy <https://github.com/tweepy/tweepy>`_ Twitter API library:
        ``pip install tweepy``

    Example:

    .. code-block :: bash

        $ python manage.py import_twitter_languages

    """
    help = "Import supported languages from the Twitter API." \
           "If the languages already exist in the database, they will not be duplicated."

    def handle(self, *args, **options):

        if twitter.tweepy_installed():

            # Get languages from Twitter
            tw_languages = twitter.get_languages()
            print "Obtained %d languages from Twitter." % len(tw_languages)

            # Convert to models and create in database
            count_created = 0
            for twlang in tw_languages:
                lang, created = corpus_models.Language.objects.get_or_create(
                    code=twlang['code'],
                    name=twlang['name'],
                )
                if created:
                    count_created += 1

            print "Imported %d languages." % count_created
            print "Database now contains %d languages." % corpus_models.Language.objects.count()

        else:
            raise Exception("Tweepy not installed! Run 'pip install tweepy'.")
