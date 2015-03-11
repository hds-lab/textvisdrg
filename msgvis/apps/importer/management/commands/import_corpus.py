from django.core.management.base import BaseCommand, CommandError
from msgvis.apps.importer.models import create_an_instance_from_json
from optparse import make_option

from msgvis.apps.corpus.models import Dataset
from django.db import transaction
import traceback
import sys
import path
from time import time
from django.conf import settings

class Command(BaseCommand):
    """
    Import a corpus of message data into the database.

    .. code-block :: bash

        $ python manage.py import_corpus <file_path>

    """
    args = '<corpus_filename> [...]'
    help = "Import a corpus into the database."
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dataset',
                    action='store',
                    dest='dataset',
                    help='Set a target dataset to add to'
        ),
    )

    def handle(self, *filenames, **options):

        if len(filenames) == 0:
            raise CommandError('At least one filename must be provided.')

        dataset = options.get('dataset', None)
        if not dataset:
            dataset = filenames[0]

        for f in filenames:
            if not path.path(f).exists():
                raise CommandError("Filename %s does not exist" % f)

        start = time()
        dataset_obj, created = Dataset.objects.get_or_create(name=dataset, description=dataset)
        if created:
            print "Created dataset '%s' (%d)" % (dataset_obj.name, dataset_obj.id)
        else:
            print "Adding to existing dataset '%s' (%d)" % (dataset_obj.name, dataset_obj.id)


        for i, corpus_filename in enumerate(filenames):
            with open(corpus_filename, 'rb') as fp:
                if len(filenames) > 1:
                    print "Reading file %d of %d %s" % (i + 1, len(filenames), corpus_filename)
                else:
                    print "Reading file %s" % corpus_filename

                importer = Importer(fp, dataset_obj)
                importer.run()

                min_time, max_time = importer.get_time_range()

                if min_time is not None and \
                    (dataset_obj.start_time is None
                     or dataset_obj.start_time > min_time):
                    dataset_obj.start_time = min_time

                if max_time is not None and \
                    (dataset_obj.end_time is None
                     or dataset_obj.end_time < max_time):
                    dataset_obj.end_time = max_time

        dataset_obj.save()

        print "Dataset '%s' (%d) contains %d messages spanning %s, from %s to %s" % (
            dataset_obj.name, dataset_obj.id, dataset_obj.message_set.count(),
            dataset_obj.end_time - dataset_obj.start_time,
            dataset_obj.start_time, dataset_obj.end_time
        )
        
        print "Time: %.2fs" % (time() - start)


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
        self.min_time = None
        self.max_time = None

    def _import_group(self, lines):
        with transaction.atomic(savepoint=False):
            for json_str in lines:

                if len(json_str) > 0:
                    try:
                        message = create_an_instance_from_json(json_str, self.dataset)
                        if message:
                            self.imported += 1

                            if self.min_time is None or self.min_time > message.time:
                                self.min_time = message.time
                            if self.max_time is None or self.max_time < message.time:
                                self.max_time = message.time
                        else:
                            self.not_tweets += 1
                    except:
                        self.errors += 1
                        print >> sys.stderr, "Import error on line %d" % self.line
                        traceback.print_exc()

        if settings.DEBUG:
            # prevent memory leaks
            from django.db import connection
            connection.queries = []


    def run(self):
        transaction_group = []

        start = time()

        for json_str in self.fp:
            self.line += 1
            json_str = json_str.strip()
            transaction_group.append(json_str)

            if len(transaction_group) >= self.commit_every:
                self._import_group(transaction_group)
                transaction_group = []

            if self.line > 0 and self.line % self.print_every == 0:
                print "%6.2fs | Reached line %d. Imported: %d; Non-tweets: %d; Errors: %d" % (
                time() - start, self.line, self.imported, self.not_tweets, self.errors)

        if len(transaction_group) >= 0:
            self._import_group(transaction_group)

        print "%6.2fs | Finished %d lines. Imported: %d; Non-tweets: %d; Errors: %d" % (
        time() - start, self.line, self.imported, self.not_tweets, self.errors)

    def get_time_range(self):
        return self.min_time, self.max_time
