from django.core.management.base import BaseCommand, CommandError

from msgvis.apps.corpus.models import Dataset, Hashtag, Url, Media

class Command(BaseCommand):
    """
    Import a corpus of message data into the database.

    .. code-block :: bash

        $ python manage.py import_corpus <file_path>

    """
    args = "<corpus_name_or_id>"

    def handle(self, corpus_name_or_id=None, *args, **options):

        if not corpus_name_or_id:
            raise CommandError("Corpus name or id must be provided")

        try:
            corpus_id = int(corpus_name_or_id)
            dataset = Dataset.objects.get(pk=corpus_id)
        except ValueError:
            dataset = Dataset.objects.get(name=corpus_name_or_id)

        print "Deleting dataset %s with %d messages and %d people..." % (dataset.name,
                                                                         dataset.message_set.count(),
                                                                         dataset.person_set.count())
        dataset.delete()

        # Now delete all the unused crap
        media = Media.objects.filter(message=None)
        print "Deleting %d unused media..." % media.count()
        media.delete()
        
        hashtags = Hashtag.objects.filter(message=None)
        print "Deleting %d unused hashtags..." % hashtags.count()
        hashtags.delete()
        urls = Url.objects.filter(message=None)
        print "Deleting %d unused urls..." % urls.count()
        urls.delete()
