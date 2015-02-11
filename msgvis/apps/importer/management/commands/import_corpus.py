from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Import a corpus of message data into the database.

    .. code-block :: bash

        $ python manage.py import_corpus ?????

    """
    help = "Import a corpus into the database."

    def handle(self, *args, **options):
        raise NotImplementedError()
