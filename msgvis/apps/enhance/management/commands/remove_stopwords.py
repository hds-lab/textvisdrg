from django.core.management.base import BaseCommand, make_option, CommandError
from msgvis.apps.corpus import models as corpus_models
import msgvis.apps.enhance.models as enhance_models
from msgvis.apps.groups import models as groups_models
from msgvis.apps.datatable import models as datatable_models
from msgvis.apps.dimensions import registry
from msgvis.apps.corpus import utils
from django.db.models import Q
import operator
import pdb

def derive_queryset(keywords_text):
    pdb.set_trace()
    return corpus_models.Dataset.objects.get(id=1).get_advanced_search_results(keywords_text, corpus_models.MessageType.objects.all())

class Command(BaseCommand):
    help = "Enter live test environment."


    def handle(self, *arguments, **options):
        '''
soup = enhance_models.TweetWord.objects.get(original_text='soup')
ladies = enhance_models.TweetWord.objects.get(original_text='ladies')
food = enhance_models.TweetWord.objects.get(original_text='food')
jobs = enhance_models.TweetWord.objects.get(original_text='jobs')

or_soup = utils.levels_or("tweet_words__id", map(lambda x: x.id, soup.related_words))
or_ladies = utils.levels_or("tweet_words__id", map(lambda x: x.id, ladies.related_words))
or_food = utils.levels_or("tweet_words__id", map(lambda x: x.id, food.related_words))
or_jobs = utils.levels_or("tweet_words__id", map(lambda x: x.id, jobs.related_words))
soup_and_ladies = reduce(operator.and_, [or_soup, or_ladies])
soup_and_ladies_or_food = reduce(operator.or_, [soup_and_ladies, or_food])

queryset = corpus_models.Dataset.objects.get(id=1).message_set.all()
        queryset = queryset.filter(soup_and_ladies_or_food)
        final = reduce(operator.and_, [soup_and_ladies_or_food, reduce(operator.not_, [or_jobs])]) # this does not work
        '''
        #import nltk
        #from nltk.corpus import stopwords
        #stopwords_list = stopwords.words('english')
        stopwords_list = ["i'm", "&", "via", "~", "+", "-", "i'll", "he's"]
        for stopword in stopwords_list:
            queryset = enhance_models.TweetWord.objects.filter(text=stopword)
            print "stopword = %s, count = %d" %(stopword, queryset.count())
            queryset.delete()


        pdb.set_trace()
