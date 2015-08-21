from django.core.management.base import BaseCommand, make_option, CommandError

class Command(BaseCommand):
    help = "From Tweet Parser results, extract words and connect with messages for a dataset."
    args = "<dataset id> <filename>"


    def handle(self, dataset_id, filename, *args, **options):


        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        from msgvis.apps.enhance.tasks import import_from_tweet_parser_results

        import_from_tweet_parser_results(dataset_id, filename)
