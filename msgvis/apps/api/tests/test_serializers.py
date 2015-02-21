from django.test import TestCase
from django.utils.timezone import now, timedelta

from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import registry as dimensions
from msgvis.apps.questions import models as questions_models
from msgvis.apps.api import serializers

from msgvis.apps.api.tests import api_time_format


class PersonSerializerTest(TestCase):
    """
    {
        "id": 2,
        "dataset": 1
        "original_id": 2568434,
        "username": "my_name",
        "full_name": "My Name"
        "language": "en",
        "replied_to_count": 25,
        "shared_count": null,
        "mentioned_count": 24,
        "friend_count": 62,
        "follower_count": 0
    }
    """

    def test_person_serialization(self):
        dataset = corpus_models.Dataset.objects.create(name="test dataset", description='description')
        person = corpus_models.Person.objects.create(dataset=dataset,
                                                     username='username',
                                                     friend_count=62)

        desired_result = {
            "id": person.pk,
            "dataset": person.dataset.pk,
            "original_id": person.original_id,
            "username": person.username,
            "full_name": person.full_name,
        }

        serializer = serializers.PersonSerializer(person)
        result = serializer.data

        self.assertDictEqual(result, desired_result)


class MessageSerializerTest(TestCase):
    """
    {
      "id": 52,
      "dataset": 2,
      "text": "Some sort of thing or other",
      "sender": {
        "id": 2,
        "dataset": 1
        "original_id": 2568434,
        "username": "my_name",
        "full_name": "My Name"
        "language": "en",
        "replied_to_count": 25,
        "shared_count": null,
        "mentioned_count": 24,
        "friend_count": 62,
        "follower_count": 0
      },
      "time": "2010-02-25T00:23:53Z"
    }
    """

    def test_message_serialization(self):
        dataset = corpus_models.Dataset.objects.create(name="test dataset", description='description')

        sender = corpus_models.Person.objects.create(dataset=dataset,
                                                     username='username')

        message = corpus_models.Message.objects.create(dataset=dataset,
                                                       time=now(),
                                                       sender=sender,
                                                       text='I am a message')

        person_result = serializers.PersonSerializer(sender).data

        # Check the keys
        desired_result = {
            'id': message.pk,
            'dataset': message.dataset.pk,
            'sender': person_result,
            'time': api_time_format(message.time),
            'text': message.text,
        }

        serializer = serializers.MessageSerializer(message)
        result = serializer.data

        self.assertDictEqual(result, desired_result)


class ArticleSerializerTest(TestCase):
    """
    {
        "id": 13,
        "authors": "Thingummy & Bob",
        "link": "http://ijn.com/3453295",
        "title": "Names and such",
        "year": "2001",
        "venue": "International Journal of Names"
    }
    """

    def test_article_serialization(self):
        article = questions_models.Article.objects.create(year=2001,
                                                          authors="Author, Author",
                                                          link="http://foo.com",
                                                          title="An article title",
                                                          venue="VENUE 2001", )
        desired_result = {
            "id": article.pk,
            "authors": article.authors,
            "link": article.link,
            "title": article.title,
            "year": article.year,
            "venue": article.venue
        }

        serializer = serializers.ArticleSerializer(article)
        result = serializer.data

        self.assertDictEqual(result, desired_result)


class QuestionSerializerTest(TestCase):
    """
    {
      "id": 5,
      "text": "What is your name?",
      "source": {
        "id": 13,
        "authors": "Thingummy & Bob",
        "link": "http://ijn.com/3453295",
        "title": "Names and such",
        "year": "2001",
        "venue": "International Journal of Names"
      },
      "dimensions": ['time', 'author_name']
    }
    """

    def setUp(self):
        article = questions_models.Article.objects.create(year=2001,
                                                          authors="Author, Author",
                                                          link="http://foo.com",
                                                          title="An article title",
                                                          venue="VENUE 2001", )

        d1 = questions_models.Question.get_dimension_key_model("hashtags")
        d2 = questions_models.Question.get_dimension_key_model("time")

        self.question = questions_models.Question.objects.create(source=article,
                                                                 text="What is your favorite color?", )
        self.question.dimensions = [d1, d2]

        article_result = serializers.ArticleSerializer(self.question.source).data

        self.serialized_representation = {
            "id": self.question.pk,
            "text": self.question.text,
            "source": article_result,
            "dimensions": [d.key for d in self.question.dimensions.all()]
        }

        # There should be NO deserialized result since questions are read-only
        self.deserialized_representation = {}

    def test_question_serialization(self):
        """Questions serialize correctly"""
        result = serializers.QuestionSerializer(self.question).data
        self.assertDictEqual(result, self.serialized_representation)

    def test_question_deserialization(self):
        """Questions deserialize correctly"""
        serializer = serializers.QuestionSerializer(data=self.serialized_representation)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, self.deserialized_representation)


class DimensionSerializerTest(TestCase):
    """
    {
      "key": "time",
      "name": "Time",
      "description": "the time the message was sent"
    }
    """

    def setUp(self):
        self.dimension = dimensions.get_dimension('time')

        self.serialized_representation = {
            'key': self.dimension.key,
            'name': self.dimension.name,
            'description': self.dimension.description,
        }

        # Should lookup exactly the same dimension
        self.deserialized_representation = self.dimension


    def test_dimension_serialization(self):
        serializer = serializers.DimensionSerializer(self.dimension)
        result = serializer.data
        self.assertDictEqual(result, self.serialized_representation)

    def test_dimension_deserialization(self):
        serializer = serializers.DimensionSerializer(data=self.serialized_representation)
        self.assertTrue(serializer.is_valid())
        self.assertEquals(serializer.validated_data, self.deserialized_representation)


class DimensionDistributionSerializerTest(TestCase):
    """
    {
      "dataset": 2,
      "dimension": "time",
      "distribution": [...]
    }
    """

    def setUp(self):
        self.dimension = dimensions.get_dimension('time')
        self.dataset = corpus_models.Dataset.objects.create(name="test dataset", description='description')

        self.serialized_representation = {
            'dataset': self.dataset.id,
            'dimension': self.dimension.key,
        }

        # Should lookup exactly the same dimension
        self.deserialized_representation = {
            'dataset': self.dataset,
            'dimension': self.dimension,
        }


    def test_dimension_distribution_serialization(self):
        distribution = [
            dict(value=2, count=5),
            dict(value=56, count=23),
            dict(value='asdf', count=53),
        ]

        self.deserialized_representation['distribution'] = distribution
        self.serialized_representation['distribution'] = distribution

        serializer = serializers.DimensionDistributionSerializer(self.deserialized_representation)
        result = serializer.data
        self.assertDictEqual(result, self.serialized_representation)

    def test_dimension_distribution_deserialization(self):
        serializer = serializers.DimensionDistributionSerializer(data=self.serialized_representation)
        self.assertTrue(serializer.is_valid())
        self.assertEquals(serializer.validated_data, self.deserialized_representation)


class QuantitativeFilterSerializerTest(TestCase):
    """
    {
      "dimension": 'reply_count',
      "max": 100
    }
    """

    def setUp(self):
        self.dimension = dimensions.get_dimension('replies')

        self.internal_filter = {
            'dimension': self.dimension,
            'min': 5,
            'max': 10,
        }

        self.external_filter = {
            'dimension': self.dimension.key,
            'min': 5,
            'max': 10,
        }

    def test_quantitative_filter_serialization(self):
        """Serialization of min and max filters"""
        result = serializers.FilterSerializer(self.internal_filter).data
        self.assertDictEqual(result, self.external_filter)

    def test_quantitative_filter_deserialization(self):
        """Deserialization of min and max filters"""
        serializer = serializers.FilterSerializer(data=self.external_filter)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, self.internal_filter)

    def test_optional_filter_params(self):
        """Min and max are optional"""
        del self.internal_filter['max']
        del self.external_filter['max']

        # Serialize
        result = serializers.FilterSerializer(self.internal_filter).data
        self.assertDictEqual(result, self.external_filter)

        # Deserialize
        serializer = serializers.FilterSerializer(data=self.external_filter)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, self.internal_filter)


class TimeFilterSerializerTest(TestCase):
    """
    {
      "dimension": 'time',
      "min_time": "2010-02-25T00:23:53Z",
      "max_time": "2010-02-30T00:23:53Z"
    }
    """

    def setUp(self):
        self.dimension = dimensions.get_dimension('time')

        self.internal_filter = {
            'dimension': self.dimension,
            'min_time': now(),
            'max_time': now() + timedelta(minutes=5),
        }

        self.external_filter = {
            'dimension': self.dimension.key,
            'min_time': api_time_format(self.internal_filter['min_time']),
            'max_time': api_time_format(self.internal_filter['max_time']),
        }

    def test_time_filter_serialization(self):
        """Serialization of min and max filters"""
        result = serializers.FilterSerializer(self.internal_filter).data
        self.assertDictEqual(result, self.external_filter)

    def test_time_filter_deserialization(self):
        """Deserialization of min and max filters"""
        serializer = serializers.FilterSerializer(data=self.external_filter)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, self.internal_filter)


class CategoricalFilterSerializerTest(TestCase):
    """
    {
      "dimension": 'words',
      "include": [
        "cat",
        "dog",
        "alligator"
      ]
    }
    """

    def setUp(self):
        self.dimension = self.dimension = dimensions.get_dimension('sentiment')

        self.internal_filter = {
            'dimension': self.dimension,
            'levels': ['a', 'b', 'c'],
        }

        self.external_filter = {
            'dimension': self.dimension.key,
            'levels': self.internal_filter['levels']
        }

    def test_categorical_filter_serialization(self):
        """Serialization of an include list"""
        result = serializers.FilterSerializer(self.internal_filter).data
        self.assertDictEqual(result, self.external_filter)

    def test_categorical_filter_deserialization(self):
        """Deserialization of an include list"""
        serializer = serializers.FilterSerializer(data=self.external_filter)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, self.internal_filter)


class DataTableSerializerTest(TestCase):
    """
    {
      "dataset": 2,
      "dimensions": ['time'],
      "filters": [...],
      "result": [...]
    }
    """

    def setUp(self):
        self.dimension = dimensions.get_dimension('time')
        self.dataset = corpus_models.Dataset.objects.create(name="test dataset", description='description')

        internal_filter = {
            'dimension': self.dimension,
            'min_time': now(),
            'max_time': now() + timedelta(minutes=5),
        }

        serialized_filter = serializers.FilterSerializer(internal_filter).data

        self.serialized_representation = {
            'dataset': self.dataset.id,
            'dimensions': [self.dimension.key],
            'filters': [serialized_filter],
        }

        # Should lookup exactly the same dimension
        self.deserialized_representation = {
            'dataset': self.dataset,
            'dimensions': [self.dimension],
            'filters': [internal_filter],
        }


    def test_dimension_distribution_serialization(self):
        datatable = [
            dict(value=2, count=5),
            dict(value=56, count=23),
            dict(value='asdf', count=53),
        ]

        self.deserialized_representation['result'] = datatable
        self.serialized_representation['result'] = datatable

        serializer = serializers.DataTableSerializer(self.deserialized_representation)
        result = serializer.data
        self.assertDictEqual(result, self.serialized_representation)

    def test_dimension_distribution_deserialization(self):
        serializer = serializers.DataTableSerializer(data=self.serialized_representation)
        self.assertTrue(serializer.is_valid())
        self.assertEquals(serializer.validated_data, self.deserialized_representation)
