from django.core.management.base import BaseCommand, CommandError
from msgvis.apps.importer.models import create_an_instance_from_json
from optparse import make_option

from msgvis.apps.corpus.models import Dataset
from django.db import transaction
import traceback

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
                            default=None,
                            help='Set a target dataset to add to'),
                        )

    def handle(self, corpus_filename, *args, **options):

        if not corpus_filename:
            raise CommandError('Corpus filename must be provided.')

        dataset = options.get('dataset')

        with open(corpus_filename, 'rb') as fp:

            if dataset is None:
                dataset_obj = Dataset.objects.create(name=corpus_filename, description=corpus_filename)
            else:
                dataset_obj, created = Dataset.objects.get_or_create(name=dataset, description=dataset)

            importer = Importer(fp, dataset_obj)
            importer.run()


class Importer(object):
    commit_every = 100
    print_every = 1000

    def __init__(self, fp, dataset):
        self.fp = fp
        self.dataset = dataset
        self.line = 0
        self.imported = 0
        self.not_tweets = 0
        self.errors = 0

    def _import_group(self, lines):
        with transaction.atomic():
            for json_str in lines:

                if len(json_str) > 0:
                    try:
                        if create_an_instance_from_json(json_str, self.dataset):
                            self.imported += 1
                        else:
                            self.not_tweets += 1
                    except:
                        self.errors += 1
                        print "Import error on line %d" % self.line
                        traceback.print_exc()

    def run(self):

        transaction_group = []

        for json_str in self.fp:
            self.line += 1
            json_str = json_str.strip()
            transaction_group.append(json_str)

            if len(transaction_group) >= self.commit_every:
                self._import_group(transaction_group)
                transaction_group = []

            if self.line > 0 and self.line % self.print_every == 0:
                print "Reached line %d. Imported: %d; Non-tweets: %d; Errors: %d" % (self.line, self.imported, self.not_tweets, self.errors)

        if len(transaction_group) >= 0:
            self._import_group(transaction_group)

        print "Finished %d lines. Imported: %d; Non-tweets: %d; Errors: %d" % (self.line, self.imported, self.not_tweets, self.errors)
