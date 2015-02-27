from django.core.management.base import BaseCommand, CommandError
from msgvis.apps.importer.models import load_research_questions_from_json

from msgvis.apps.corpus.models import Dataset


class Command(BaseCommand):
    """
    Import research questions into the database.

    .. code-block :: bash

        $ python manage.py import_questions <file_path>

    """
    args = '<research_questions_filename>'
    help = "Import research questions into the database."

    def handle(self, filename, *args, **options):
        if not filename:
            raise CommandError('Research questions filename must be provided.')

        fp = open(filename, 'r')
        json_str = fp.read()
        load_research_questions_from_json(json_str)
