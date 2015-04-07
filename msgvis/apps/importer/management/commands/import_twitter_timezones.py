from django.core.management.base import BaseCommand, CommandError

from msgvis.apps.importer import twitter
from msgvis.apps.corpus import models as corpus_models
from path import path

class Command(BaseCommand):
    """
    Obtains a mapping of the Twitter-supported timezones from the Ruby on Rails TimeZone class.

    Get the mapping dictionary from https://github.com/rails/rails/blob/master/activesupport/lib/active_support/values/time_zone.rb

    .. note::

        Requires `Ruby on Rails <http://rubyonrails.org/download/>`_ to be installed: ``gem install rails``.

    Example:

    .. code-block :: bash

        $ python manage.py import_twitter_timezones setup/time_zone_mapping.rb

    """
    help = "Import Twitter-supported timezones from the Ruby on Rails TimeZone class."
    args = '<time_zone_mapping.rb>'

    def handle(self, time_zone_file=None, *args, **options):

        if not time_zone_file:
            raise CommandError("Copy the MAPPING from https://github.com/rails/rails/blob/master/activesupport/lib/active_support/values/time_zone.rb")

        time_zone_file = path(time_zone_file)
        if not time_zone_file.exists():
            raise CommandError('Time zone file "%s" does not exist' % time_zone_file)

        # Get languages from Twitter
        timezones = twitter.get_timezones(time_zone_file)
        ncreated = 0
        for name, olson in timezones:
            tz, created = corpus_models.Timezone.objects.get_or_create(
                name=name,
                olson_code=olson,
            )
            if created:
                ncreated += 1
        print "Imported %d timezones." % ncreated
