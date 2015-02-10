from django.test import TestCase
from django.utils.timezone import now, timedelta

from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.questions import models as questions_models
from msgvis.apps.dimensions import models as dimensions_models
import serializers


def api_time_format(dt):
    """Convert a datetime to string according to the API settings"""
    from rest_framework.fields import DateTimeField

    field = DateTimeField()
    return field.to_representation(dt)


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
      "dimensions": [4, 5]
    }
    """

    def test_question_serialization(self):
        article = questions_models.Article.objects.create(year=2001,
                                                          authors="Author, Author",
                                                          link="http://foo.com",
                                                          title="An article title",
                                                          venue="VENUE 2001", )

        d1 = dimensions_models.Dimension.objects.create(name="something", description="longer something")
        d2 = dimensions_models.Dimension.objects.create(name="else", description="something else")

        question = questions_models.Question.objects.create(source=article,
                                                            text="What is your favorite color?", )
        question.dimensions = [d1, d2]

        article_result = serializers.ArticleSerializer(article).data

        desired_result = {
            "id": question.pk,
            "text": question.text,
            "source": article_result,
            "dimensions": [d1.pk, d2.pk]
        }

        serializer = serializers.QuestionSerializer(question)
        result = serializer.data

        self.assertDictEqual(result, desired_result)


class DimensionSerializerTest(TestCase):
    """
    {
      "id": 5,
      "name": "time",
      "description": "the time the message was sent",
      "scope": "open",
      "type": "quantitative",
    }
    """

    def test_dimension_serialization(self):
        dimension = dimensions_models.Dimension.objects.create(name="something", description="longer something")

        desired_result = {
            'id': dimension.pk,
            'name': dimension.name,
            'description': dimension.description,
            'scope': dimension.scope,
            'type': dimension.type,
        }

        serializer = serializers.DimensionSerializer(dimension)
        result = serializer.data

        self.assertDictEqual(result, desired_result)


class QuantitativeFilterSerializerTest(TestCase):
    def setUp(self):
        self.dimension = dimensions_models.Dimension.objects.create(name="something", description="longer something")

        self.internal_filter = {
            'dimension': self.dimension,
            'min': 5,
            'max': 10,
        }

        self.external_filter = {
            'dimension': self.dimension.pk,
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
    def setUp(self):
        self.dimension = dimensions_models.Dimension.objects.create(name="something", description="longer something")

        self.internal_filter = {
            'dimension': self.dimension,
            'min_time': now(),
            'max_time': now() + timedelta(minutes=5),
        }

        self.external_filter = {
            'dimension': self.dimension.pk,
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
    def setUp(self):
        self.dimension = dimensions_models.Dimension.objects.create(name="something", description="longer something")

        self.internal_filter = {
            'dimension': self.dimension,
            'include': ['a', 'b', 'c'],
        }

        self.external_filter = {
            'dimension': self.dimension.pk,
            'include': self.internal_filter['include']
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
