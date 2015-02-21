from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status

from django.utils import timezone as tz

from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.questions import models as questions_models
from msgvis.apps.dimensions import models as dimensions_models
import mock

from msgvis.apps.api.tests import api_time_format


class DimensionDistributionViewTest(APITestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Api test dataset")

    @mock.patch('msgvis.apps.dimensions.registry.get_dimension')
    def test_get_distribution_api(self, get_dimension):
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

        expected_response = {
            "dataset": self.dataset.id,
            "dimension": dimension.key,
            "distribution": distribution
        }

        response = self.client.post(url, data, format='json')

        self.assertEquals(response.data, expected_response)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        get_dimension.assert_called_once_with(dimension.key)
        dimension.get_distribution.assert_called_once_with(self.dataset)



class ResearchQuestionsViewTest(APITestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Api test dataset")

        # Create some dimension keys
        self.dimension_keys = ['time', 'hashtags']
        primary_dim = dimensions_models.DimensionKey.objects.create(key=self.dimension_keys[0])
        secondary_dim = dimensions_models.DimensionKey.objects.create(key=self.dimension_keys[1])

        # Create an article
        article = questions_models.Article.objects.create(
            authors="something",
            link="a link",
            title="some title",
            venue="a venue"
        )

        # Generate some sample research questions
        self.sample_questions = [
            questions_models.Question.objects.create(
                text="hello",
                source=article,
            ),
            questions_models.Question.objects.create(
                text="goodbye",
                source=article,
            ),
        ]

        for q in self.sample_questions:
            q.dimensions.add(primary_dim)
            q.dimensions.add(secondary_dim)

    @mock.patch('msgvis.apps.questions.models.Question.get_sample_questions')
    def test_get_sample_questions_api(self, get_sample_questions):
        primary_dimension_key = self.dimension_keys[0]
        secondary_dimension_key = self.dimension_keys[1]

        get_sample_questions.return_value = self.sample_questions

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
                } for q in self.sample_questions
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEquals(response.data, expected_response)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        get_sample_questions.assert_called_once_with(primary_dimension_key, secondary_dimension_key)


class ExampleMessagesViewTest(APITestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Api test dataset")

        sender = self.dataset.person_set.create(
            username='a person',
            full_name='a more important person',
            original_id=2353583,
        )

        # Create a couple of messages
        self.sample_messages = [
            self.dataset.message_set.create(
                text="i am a message",
                time=tz.now(),
                sender=sender,
            ),
            self.dataset.message_set.create(
                text="another message",
                time=tz.now(),
                sender=sender,
            )
        ]


    @mock.patch('msgvis.apps.corpus.models.Dataset.get_example_messages')
    def test_get_example_messages_api(self, get_example_messages):
        # fake the actual example finding
        get_example_messages.return_value = self.sample_messages

        url = reverse('example-messages')
        data = {
            "filters": [
                {
                    "dimension": "time",
                    "min_time": "2015-02-02T01:19:08Z",
                    "max_time": "2015-02-02T01:19:09Z"
                }
            ],
            "focus": [
                {
                    "dimension": "time",
                    "value": "2015-02-02T01:19:09Z"
                }
            ]
        }

        expected_response = {
            "filters": data['filters'],
            "focus": data['focus'],
            "messages": [
                {
                    'id': m.id,
                    'dataset': m.dataset_id,
                    'text': m.text,
                    'time': api_time_format(m.time),
                    'sender': {
                        'id': m.sender.id,
                        'dataset': m.sender.dataset_id,
                        'original_id': m.sender.original_id,
                        'username': m.sender.username,
                        'full_name': m.sender.full_name,
                    }
                } for m in self.sample_messages
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEquals(response.data, expected_response)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertEquals(get_example_messages.call_count, 1)

class DataTableViewTest(APITestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Api test dataset")

        sender = self.dataset.person_set.create(
            username='a person',
            full_name='a more important person',
            original_id=2353583,
        )

        # Create a couple of messages
        self.sample_messages = [
            self.dataset.message_set.create(
                text="i am a message",
                sender=sender,
            ),
            self.dataset.message_set.create(
                text="another message",
                sender=sender,
            )
        ]

    @mock.patch('msgvis.apps.dimensions.registry.get_dimension')
    @mock.patch('msgvis.apps.datatable.models.DataTable')
    def test_get_datatable_api(self, DataTable, get_dimension):

        # Provide a fake dimension
        dimension = get_dimension.return_value
        dimension.key = 'time'

        # Fake the filtered queryset
        filtered_queryset = dimension.filter.return_value

        # Fake the data table itself
        fake_datatable = [
            {
                "value": 35,
                "time": "2010-02-25T00:23:53Z"
            },
            {
                "value": 30,
                "time": "2010-02-26T00:23:53Z"
            },
            {
                "value": 25,
                "time": "2010-02-27T00:23:53Z"
            },
            {
                "value": 20,
                "time": "2010-02-28T00:23:53Z"
            }
        ]
        table_instance = DataTable.return_value
        table_instance.render.return_value = fake_datatable

        url = reverse('data-table')
        data = {
            "dataset": self.dataset.id,
            "dimensions": ['time'],
            "filters": [
                {
                    "dimension": 'time',
                    "min_time": "2010-02-25T00:23:53Z",
                    "max_time": "2010-02-28T00:23:53Z"
                }
            ],
        }

        expected_response = {
            'dataset': self.dataset.id,
            "dimensions": data['dimensions'],
            "filters": data['filters'],
            "result": fake_datatable,
        }

        response = self.client.post(url, data, format='json')

        # And it should have rendered appropriately
        self.assertEquals(response.data, expected_response)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # It should have constructed a datatable for the dimension
        DataTable.assert_called_once_with(dimension)

        # It should have then given the filtered queryset to the data table
        table_instance.render.assert_called_once_with(filtered_queryset)
