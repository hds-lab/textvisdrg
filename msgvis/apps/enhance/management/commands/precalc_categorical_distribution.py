from django.core.management.base import BaseCommand, make_option, CommandError
import sys
from django.db import transaction

class Command(BaseCommand):
    help = "Extract topics for a dataset."
    args = "<dataset id>"


    def handle(self, dataset_id, *args, **options):

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        from msgvis.apps.enhance.tasks import precalc_categorical_dimension
        #categorical_dimensions = ["hashtags", "words", "urls", "timezone", "contains_media", "sentiment", "type", "sender", "mentions"]
        categorical_dimensions = ["hashtags", "urls", "timezone", "contains_media", "sentiment", "type", "sender", "mentions"]
        #categorical_dimensions = ["words"]
        for dimension_key in categorical_dimensions:
            print >>sys.stderr, "Precalculating %s..." %(dimension_key)
            with transaction.atomic(savepoint=False):
                precalc_categorical_dimension(dataset_id=dataset_id, dimension_key=dimension_key)


