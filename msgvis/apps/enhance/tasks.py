import logging

from models import Dictionary, MessageWord, Word, MessageTopic
from msgvis.apps.corpus.models import Dataset


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
    def __init__(self, texts=None, stoplist=None):
        self.texts = texts
        self.stoplist = stoplist
        self.max_length = Word._meta.get_field('text').max_length
        if self.stoplist is None:
            self.stoplist = []

    def __iter__(self):
        if self.texts is None:
            raise RuntimeError("Tokenizer can only iterate if given texts")

        for text in self.texts:
            yield self.tokenize(text)

    def tokenize(self, text):
        words = []
        for word in self.split(text.lower()):
            if word not in self.stoplist:
                if len(word) >= self.max_length:
                    word = word[:self.max_length - 1]
                words.append(word)
        return words

    def split(self, text):
        return text.split()


class WordTokenizer(Tokenizer):
    def __init__(self, texts=None, stoplist=None):
        super(WordTokenizer, self).__init__(texts, stoplist)

        import nltk

        self._tokenize = nltk.word_tokenize

    def split(self, text):
        return self._tokenize(text)


class TopicContext(object):
    def __init__(self, name, queryset, tokenizer, minimum_frequency=2, stoplist=None):
        self.name = name
        self.queryset = queryset
        self.tokenizer = tokenizer
        self.stoplist = stoplist
        self.minimum_frequency = minimum_frequency

    def queryset_str(self):
        return str(self.queryset.query)

    def get_dict_settings(self):
        settings = dict(
            name=self.name,
            tokenizer=self.tokenizer.__name__,
            dataset=self.queryset_str(),
            stoplist=self.stoplist is not None,
            minimum_frequency=self.minimum_frequency
        )

        import json

        return json.dumps(settings, sort_keys=True)


    def find_dictionary(self):
        results = Dictionary.objects.filter(settings=self.get_dict_settings())
        return results.last()


    def build_dictionary(self):
        texts = DbTextIterator(self.queryset)

        tokenized_texts = self.tokenizer(texts, stoplist=self.stoplist)

        return Dictionary._create_from_texts(tokenized_texts=tokenized_texts,
                                             name=self.name,
                                             minimum_frequency=self.minimum_frequency,
                                             dataset=self.queryset.model.__name__,
                                             settings=self.get_dict_settings())

    def bows_exist(self, dictionary):
        return MessageWord.objects.filter(dictionary=dictionary).exists()


    def build_bows(self, dictionary):
        texts = DbTextIterator(self.queryset)
        tokenized_texts = self.tokenizer(texts, stoplist=self.stoplist)

        dictionary._vectorize_corpus(queryset=self.queryset,
                                     tokenizer=tokenized_texts)

    def build_lda(self, dictionary, num_topics=30):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._build_lda(self.name, corpus, num_topics=num_topics)

    def apply_lda(self, dictionary, model, lda=None):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._apply_lda(model, corpus, lda=lda)

    def evaluate_lda(self, dictionary, model, lda=None):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._evaluate_lda(model, corpus, lda=lda)


def standard_topic_pipeline(context, num_topics):
    dictionary = context.find_dictionary()
    if dictionary is None:
        dictionary = context.build_dictionary()

    if not context.bows_exist(dictionary):
        context.build_bows(dictionary)

    model, lda = context.build_lda(dictionary, num_topics=num_topics)
    context.apply_lda(dictionary, model, lda)
    context.evaluate_lda(dictionary, model, lda)


def default_topic_context(name, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    queryset = dataset.message_set.filter(language__code='en')

    return TopicContext(name=name, queryset=queryset,
                        tokenizer=WordTokenizer,
                        stoplist=get_stoplist(),
                        minimum_frequency=4)
