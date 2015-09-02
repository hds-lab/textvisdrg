import logging

from models import Dictionary, MessageWord, Word, MessageTopic, TweetWord, PrecalcCategoricalDistribution
from msgvis.apps.corpus.models import Dataset, Message
from msgvis.apps.dimensions import registry
from msgvis.apps.datatable import models as datatable_models
import codecs, re


logger = logging.getLogger(__name__)

__all__ = ['get_twitter_context', 'get_chat_context', 'Dictionary']

_stoplist = None


def get_stoplist():
    global _stoplist
    if not _stoplist:
        from nltk.corpus import stopwords

        _stoplist = stopwords.words('english')
    return _stoplist


class DbTextIterator(object):
    def __init__(self, queryset):
        self.queryset = queryset
        self.current_position = 0
        self.current = None

    def __iter__(self):
        self.current_position = 0
        for msg in self.queryset.iterator():
            self.current = msg
            self.current_position += 1
            if self.current_position % 10000 == 0:
                logger.info("Iterating through database texts: item %d" % self.current_position)

            yield msg.text


class DbWordVectorIterator(object):
    def __init__(self, dictionary, freq_field='tfidf'):
        self.dictionary = dictionary
        self.freq_field = freq_field
        self.current_message_id = None
        self.current_vector = None

    def __iter__(self):
        qset = MessageWord.objects.filter(dictionary=self.dictionary).order_by('message')
        self.current_message_id = None
        self.current_vector = []
        current_position = 0
        for mw in qset.iterator():
            message_id = mw.message_id
            word_idx = mw.word_index
            freq = getattr(mw, self.freq_field)

            if self.current_message_id is None:
                self.current_message_id = message_id
                self.current_vector = []

            if self.current_message_id != message_id:
                yield self.current_vector
                self.current_vector = []
                self.current_message_id = message_id
                current_position += 1

                if current_position % 10000 == 0:
                    logger.info("Iterating through database word-vectors: item %d" % current_position)

            self.current_vector.append((word_idx, freq))

        # one more extra one
        yield self.current_vector

    def __len__(self):
        from django.db.models import Count

        count = MessageWord.objects \
            .filter(dictionary=self.dictionary) \
            .aggregate(Count('message', distinct=True))

        if count:
            return count['message__count']


class Tokenizer(object):
    def __init__(self, texts, *filters):
        """
        Filters is a list of objects which can be used like sets
        to determine if a word should be removed: if word in filter, then word will
        be ignored.
        """
        self.texts = texts
        self.filters = filters
        self.max_length = Word._meta.get_field('text').max_length

    def __iter__(self):
        if self.texts is None:
            raise RuntimeError("Tokenizer can only iterate if given texts")

        for text in self.texts:
            yield self.tokenize(text)

    def tokenize(self, text):
        words = []

        for word in self.split(text.lower()):
            filter_out = False
            for f in self.filters:
                if word in f:
                    filter_out = True
                    break

            if filter_out:
                # skip this word
                continue

            if len(word) >= self.max_length:
                word = word[:self.max_length - 1]

            words.append(word)

        return words

    def split(self, text):
        return text.split()


class WordTokenizer(Tokenizer):
    def __init__(self, *args, **kwargs):
        super(WordTokenizer, self).__init__(*args, **kwargs)

        import nltk

        self._tokenize = nltk.word_tokenize

    def split(self, text):
        return self._tokenize(text)


class SimpleTokenizer(Tokenizer):
    def __init__(self, *args, **kwargs):
        super(SimpleTokenizer, self).__init__(*args, **kwargs)

        from nltk.tokenize import sent_tokenize, wordpunct_tokenize
        self._sent_tokenize = sent_tokenize
        self._tokenize = wordpunct_tokenize

        import re
        self._strip_punct = re.compile(r'[^\w\s]')

    def split(self, text):
        # split into sentence, then remove all punctuation
        sents = (self._strip_punct.sub('', sent) for sent in self._sent_tokenize(text))
        # then split on non-words
        return [token for sent in sents for token in self._tokenize(sent)]


class TopicContext(object):
    def __init__(self, name, queryset, tokenizer, filters, minimum_frequency=2):
        self.name = name
        self.queryset = queryset
        self.tokenizer = tokenizer
        self.filters = filters
        self.minimum_frequency = minimum_frequency

    def queryset_str(self):
        return str(self.queryset.query)

    def get_dict_settings(self):
        settings = dict(
            name=self.name,
            tokenizer=self.tokenizer.__name__,
            dataset=self.queryset_str(),
            filters=repr(self.filters),
            minimum_frequency=self.minimum_frequency
        )

        import json

        return json.dumps(settings, sort_keys=True)


    def find_dictionary(self):
        results = Dictionary.objects.filter(settings=self.get_dict_settings())
        return results.last()


    def build_dictionary(self, dataset_id):
        texts = DbTextIterator(self.queryset)

        tokenized_texts = self.tokenizer(texts, *self.filters)
        dataset = Dataset.objects.get(pk=dataset_id)
        return Dictionary._create_from_texts(tokenized_texts=tokenized_texts,
                                             name=self.name,
                                             minimum_frequency=self.minimum_frequency,
                                             dataset=dataset,
                                             settings=self.get_dict_settings())

    def bows_exist(self, dictionary):
        return MessageWord.objects.filter(dictionary=dictionary).exists()


    def build_bows(self, dictionary):
        texts = DbTextIterator(self.queryset)
        tokenized_texts = self.tokenizer(texts, *self.filters)

        dictionary._vectorize_corpus(queryset=self.queryset,
                                     tokenizer=tokenized_texts)

    def build_lda(self, dictionary, num_topics=30, **kwargs):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._build_lda(self.name, corpus, num_topics=num_topics, **kwargs)

    def apply_lda(self, dictionary, model, lda=None):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._apply_lda(model, corpus, lda=lda)

    def evaluate_lda(self, dictionary, model, lda=None):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._evaluate_lda(model, corpus, lda=lda)


class LambdaWordFilter(object):
    def __init__(self, fn):
        self.fn = fn

    def __contains__(self, item):
        return self.fn(item)


def standard_topic_pipeline(context, dataset_id, num_topics, **kwargs):
    dictionary = context.find_dictionary()
    if dictionary is None:
        dictionary = context.build_dictionary(dataset_id=dataset_id)

    if not context.bows_exist(dictionary):
        context.build_bows(dictionary)

    model, lda = context.build_lda(dictionary, num_topics=num_topics, **kwargs)
    context.apply_lda(dictionary, model, lda)
    context.evaluate_lda(dictionary, model, lda)


def default_topic_context(name, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    queryset = dataset.message_set.filter(language__code='en')

    filters = [
        set(get_stoplist()),
        LambdaWordFilter(lambda word: word.startswith('http') and len(word) > 4)
    ]

    return TopicContext(name=name, queryset=queryset,
                        tokenizer=SimpleTokenizer,
                        filters=filters,
                        minimum_frequency=4)


def import_from_tweet_parser_results(dataset_id, filename):
    current_msg_id = -1
    current_msg = None
    word_list = []
    with codecs.open(filename, encoding='utf-8', mode='r') as f:
        for line in f:
            if re.search("ID=(\d+)", line):

                # save the previous word list
                if len(word_list) > 0:
                    current_msg.tweet_words.add(*word_list)
                    word_list = []

                results = re.match('ID=(\d+)', line)
                groups = results.groups()
                current_msg_id = int(groups[0])
                print "current msg id = %d" %(current_msg_id)
                current_msg = Message.objects.get(id=current_msg_id)


            elif re.search("(.+)\t(.+)\t(.+)", line):
                results = re.match('(.+)\t(.+)\t(.+)', line)
                groups = results.groups()
                pos = groups[1]
                word = groups[2]
                if re.search('[,~U]', pos):
                    continue
                else:
                    word_obj, created = TweetWord.objects.get_or_create(dataset_id=dataset_id, text=word)
                    word_list.append(word_obj)
        # save the previous word list
        if len(word_list) > 0:
            current_msg.tweet_words.add(*word_list)
            word_list = []

def precalc_categorical_dimension(dataset_id=1, dimension_key=None):
    datatable = datatable_models.DataTable(primary_dimension=dimension_key)
    dataset = Dataset.objects.get(id=dataset_id)

    # remove existing calculation
    PrecalcCategoricalDistribution.objects.filter(dimension_key=dimension_key).delete()

    result = datatable.generate(dataset)
    bulk = []
    for bucket in result["table"]:
        level = bucket[dimension_key]
        if level is None:
            level = ""
        count = bucket["value"]
        obj = PrecalcCategoricalDistribution(dataset=dataset, dimension_key=dimension_key, level=level, count=count)
        bulk.append(obj)

    PrecalcCategoricalDistribution.objects.bulk_create(objs=bulk, batch_size=10000)

