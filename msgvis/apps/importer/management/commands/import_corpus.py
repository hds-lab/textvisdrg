from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Import a corpus into the database."

    def handle(self, *args, **options):
        raise NotImplementedError()
