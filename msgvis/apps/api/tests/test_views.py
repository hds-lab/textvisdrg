from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status

from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.questions import models as questions_models
from msgvis.apps.dimensions import models as dimensions_models
import mock


class DimensionDistributionViewTest(APITestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Api test dataset")

    @mock.patch('msgvis.apps.dimensions.registry.get_dimension')
    def test_get_count_distribution(self, get_dimension):
        # Fake the dimension internally
        dimension = mock.Mock()
        dimension.key = 'time'
        get_dimension.return_value = dimension

        # Fake the distribution too
        distribution = [
            {
                "count": 5000,
                "value": "cat"
            },
            {
                "count": 1000,
                "value": "catch"
            },
            {
                "count": 500,
                "value": "cathedral"
            },
            {
                "count": 50,
                "value": "cataleptic"
            }
        ]
        dimension.get_distribution.return_value = distribution

        url = reverse('dimension-distribution')
        data = {
            "dataset": self.dataset.id,
            "dimension": dimension.key,
        }

        response = self.client.post(url, data, format='json')

        expected_response = {
            "dataset": self.dataset.id,
            "dimension": dimension.key,
            "distribution": distribution
        }

        get_dimension.assert_called_once_with(dimension.key)
        dimension.get_distribution.assert_called_once_with(self.dataset)
        self.assertEquals(response.data, expected_response)
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class ResearchQuestionsViewTest(APITestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Api test dataset")

    @mock.patch('msgvis.apps.questions.models.Question.get_sample_questions')
    def test_get_count_distribution(self, get_sample_questions):
        primary_dimension_key = 'time'
        secondary_dimension_key = 'hashtags'

        # Mock the sample questions (sadly this requires a ton of models)
        article = questions_models.Article.objects.create(
            authors="something",
            link="a link",
            title="some title",
            venue="a venue"
        )
        primary_dim = dimensions_models.DimensionKey.objects.create(key=primary_dimension_key)
        secondary_dim = dimensions_models.DimensionKey.objects.create(key=secondary_dimension_key)
        sample_questions = [
            questions_models.Question.objects.create(
                text="hello",
                source=article,
            ),
            questions_models.Question.objects.create(
                text="goodbye",
                source=article,
            ),
        ]
        for q in sample_questions:
            q.dimensions.add(primary_dim)
            q.dimensions.add(secondary_dim)

        get_sample_questions.return_value = sample_questions

        url = reverse('research-questions')
        data = {
            "dimensions": [primary_dimension_key, secondary_dimension_key]
        }

        expected_response = {
            'dimensions': [primary_dimension_key, secondary_dimension_key],
            'questions': [
                {
                    'id': q.id,
                    'text': q.text,
                    'dimensions': [d.key for d in q.dimensions.all()],
                    'source': {
                        'id': q.source.id,
                        'authors': q.source.authors,
                        'link': q.source.link,
                        'title': q.source.title,
                        'year': q.source.year,
                        'venue': q.source.venue,
                    }
                } for q in sample_questions
            ]
        }

        response = self.client.post(url, data, format='json')

        get_sample_questions.assert_called_once_with(primary_dimension_key, secondary_dimension_key)

        self.assertEquals(response.data, expected_response)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

