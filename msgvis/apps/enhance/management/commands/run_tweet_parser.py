from django.core.management.base import BaseCommand, make_option, CommandError
from time import time
import path
from django.db import transaction
import os

def check_or_create_dir(dir_path):
    if os.path.exists(dir_path):
            if not os.path.isdir(dir_path):
                raise CommandError("The given path is not a folder.")
    else:
        try:
            os.mkdir(dir_path)
        except OSError:
            raise CommandError("Weird path error happens.")

class Command(BaseCommand):
    help = "Run tweet parser on a dataset. Results will be saved into files."
    args = '<dataset_id> <file_save_path>'
    option_list = BaseCommand.option_list + (
        make_option('-a', '--action',
                    default='all',
                    dest='action',
                    help='Action to run [all | dump | parse | lemmatize]'
        ),
        make_option('-p', '--path',
                    default='/home/vagrant/textvisdrg/datasets/ark-tweet-nlp-0.3.2',
                    dest='tweet_parser_path',
                    help='Tweet parser path'
        ),
    )


    def handle(self, dataset_id, save_path, **options):
        action = options.get('action')
        tweet_parser_path = options.get('tweet_parser_path')

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        if not save_path:
            raise CommandError("File save path is required.")

        check_or_create_dir(save_path)

        if action == 'all' or action == 'dump':
            from msgvis.apps.enhance.tasks import dump_tweets
            dump_tweets(dataset_id, save_path)

        if action == 'all' or action == 'parse':
            from msgvis.apps.enhance.tasks import parse_tweets
            output_path = "%s/parsed_tweets" %save_path
            check_or_create_dir(output_path)

            parse_tweets(tweet_parser_path, save_path, output_path)

        if action == 'all' or action == 'lemmatize':
            from msgvis.apps.enhance.tasks import lemmatize_tweets
            input_path = "%s/parsed_tweets" %save_path
            output_path = "%s/converted_tweets" %save_path
            check_or_create_dir(output_path)

            lemmatize_tweets(input_path, output_path)
