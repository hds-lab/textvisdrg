from django.core.management.base import BaseCommand, make_option, CommandError
from time import time
import path
from django.db import transaction

class Command(BaseCommand):
    help = "From Tweet Parser results, extract words and connect with messages for a dataset."
    args = '<dataset_id> <parsed_filename> [...]'

    def handle(self, dataset_id, *filenames, **options):

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        if len(filenames) == 0:
            raise CommandError('At least one filename must be provided.')

        for f in filenames:
            if not path.path(f).exists():
                raise CommandError("Filename %s does not exist" % f)

        from msgvis.apps.enhance.tasks import import_from_tweet_parser_results
        start = time()
        for i, parsed_tweet_filename in enumerate(filenames):
            if len(filenames) > 1:
                print "Reading file %d of %d %s" % (i + 1, len(filenames), parsed_tweet_filename)
            else:
                print "Reading file %s" % parsed_tweet_filename

            with transaction.atomic(savepoint=False):
                import_from_tweet_parser_results(dataset_id, parsed_tweet_filename)

        print "Time: %.2fs" % (time() - start)