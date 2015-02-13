from django.core.management.base import BaseCommand
from msgvis.apps.importer.models import create_an_instance_from_json

from msgvis.apps.corpus.models import Dataset


class Command(BaseCommand):
    """
    Import a corpus of message data into the database.

    .. code-block :: bash

        $ python manage.py import_corpus <file_path>

    """
    help = "Import a corpus into the database."

    def handle(self, *args, **options):
        if len(args) == 0:
            return False # TODO: replace with exception

        fp = open(args[0], 'r')
        dataset_obj = Dataset.objects.create(name=args[0], description=args[0])
        for json_str in iter(lambda: fp.readline(), ''):
            json_str = json_str.rstrip('\r\n')
            if len(json_str) > 0:
                create_an_instance_from_json(json_str, dataset_obj)
