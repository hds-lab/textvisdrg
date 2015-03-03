from django.core.management.base import BaseCommand, CommandError
from msgvis.apps.importer.models import create_an_instance_from_json
from optparse import make_option

from msgvis.apps.corpus.models import Dataset


class Command(BaseCommand):
    """
    Import a corpus of message data into the database.

    .. code-block :: bash

        $ python manage.py import_corpus <file_path>

    """
    args = '<corpus_filename>'
    help = "Import a corpus into the database."
    option_list = BaseCommand.option_list + (
                        make_option('-d', '--dataset',
                            action='store',
                            dest='dataset',
                            default=False,
                            help='Set a target dataset to add to'),
                        )

    def handle(self, corpus_filename, *args, **options):

        if not corpus_filename:
            raise CommandError('Corpus filename must be provided.')

        dataset = options.get('dataset')

        fp = open(corpus_filename, 'r')
        if dataset is None:
            dataset_obj = Dataset.objects.create(name=corpus_filename, description=corpus_filename)
        else:
            dataset_obj, created = Dataset.objects.get_or_create(name=dataset, description=dataset)

        for json_str in iter(lambda: fp.readline(), ''):
            json_str = json_str.rstrip('\r\n')
            if len(json_str) > 0:
                create_an_instance_from_json(json_str, dataset_obj)
