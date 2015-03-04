from django.test import TestCase

from msgvis.apps.enhance import models, tasks
from msgvis.apps.corpus import models as corpus_models


class MessageSentimentTest(TestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")

    def test_sentiment(self):
        """Dataset.created_at should get set automatically."""
        msg = self.dataset.message_set.create(
            text="kitties are the worst awfullest animals and i hate them"
        )
        models.set_message_sentiment(msg)
        self.assertEquals(msg.sentiment, corpus_models.Message.SENTIMENT_NEGATIVE)


class TopicsTest(TestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")

        self.dictionary = models.Dictionary.objects.create(
            name="test dictionary",
            dataset="test dataset",
        )

        self.topic_model = self.dictionary.topicmodel_set.create(
            name="test topic model",
            description="test topic model",
        )

        self.topic = self.topic_model.topics.create(
            name="test topic",
            description="test topic",
            index=0,
            alpha=0
        )

    def test_get_topics_no_topics(self):
        """When there are no topics, should return empty list of topics"""

        msg = self.dataset.message_set.create(
            text="kitties are the worst awfullest animals and i hate them"
        )

        self.assertEquals(msg.topics.count(), 0)

    def test_get_topics_with_topics(self):
        """If the message has topics, should return them"""

        msg = self.dataset.message_set.create(
            text="kitties are the worst awfullest animals and i hate them"
        )

        models.MessageTopic.objects.create(
            topic_model=self.topic_model,
            topic=self.topic,
            probability=0.5,
            message=msg,
        )

        self.assertEquals(msg.topics.count(), 1)
        topic = msg.topics.first()
        self.assertIsInstance(topic, models.Topic)

    def test_topic_modeling(self):
        """Generate some test messages and actually model topics"""

        randomseed = 1
        from numpy import random as nprandom
        import random
        nprandom.seed(randomseed)
        random.seed(randomseed)

        n_messages = 50
        n_words = 5
        num_topics = 2

        topic_a_vocab = ['cat', 'hat', 'marbles']
        topic_b_vocab = ['oppossum', 'lasso', 'amalgam']
        total_words = len(topic_a_vocab) + len(topic_b_vocab)

        english, created = corpus_models.Language.objects.get_or_create(code='en', name="English")

        for i in xrange(n_messages):
            if i < n_messages / 2:
                vocab = topic_a_vocab
            else:
                vocab = topic_b_vocab

            self.dataset.message_set.create(
                text=" ".join(random.choice(vocab) for w in xrange(n_words)),
                language=english,
            )

        context = tasks.default_topic_context("test_topic_modeling", dataset_id=self.dataset.id)
        tasks.standard_topic_pipeline(context, num_topics=num_topics, multicore=False)

        dictionary = models.Dictionary.objects.get(name='test_topic_modeling')

        # Check the basic stats of the dictionary
        self.assertEquals(dictionary.num_docs, n_messages)
        self.assertEquals(dictionary.num_pos, n_messages * n_words)

        # Check the links to words
        self.assertEquals(dictionary.words.count(), total_words)

        # Check the links to topic models
        self.assertEquals(dictionary.topicmodel_set.count(), 1)
        topic_model = dictionary.topicmodel_set.first()
        self.assertLess(topic_model.perplexity, -1)

        # Check the number of topics
        self.assertEquals(topic_model.topics.count(), num_topics)
        topics = topic_model.topics.all()
        topic_a = topics[0]
        topic_b = topics[1]

        # Should be the proper number of messages with positive topic probabilities
        # The - 3 factor on the end allows a little wiggle room for randomness

        # Count the messages that prefer each topic
        from collections import defaultdict
        topic_count = defaultdict(int)
        for msg in self.dataset.message_set.all():
            topic = topic_model.get_probable_topic(msg)
            topic_count[topic] += 1

        self.assertEquals(topic_count, {
            topic_a: n_messages / 2,
            topic_b: n_messages / 2,
        })


