from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status

from django.utils import timezone as tz
from django.db.models import query

from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.questions import models as questions_models
from msgvis.apps.dimensions import models as dimensions_models
import mock

from msgvis.apps.api.tests import api_time_format, django_time_format


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
            q.add_dimension(primary_dim)
            q.add_dimension(secondary_dim)

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


    @mock.patch.object(corpus_models.Dataset, 'get_example_messages')
    def test_get_example_messages_api(self, get_example_messages):
        # fake the actual example finding
        get_example_messages.return_value = self.sample_messages

        url = reverse('example-messages')
        data = {
            "dataset": self.dataset.id,
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
            "dataset": data['dataset'],
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
                    },
                    'original_id': None,
                    'embedded_html': u'<blockquote class="twitter-tweet" data-cards="hidden" > <p lang="en" dir="ltr">Sunsets don&#39;t get much better than this one over <a href="https://twitter.com/GrandTetonNPS">@GrandTetonNPS</a>. <a href="https://twitter.com/hashtag/nature?src=hash">#nature</a> <a href="https://twitter.com/hashtag/sunset?src=hash">#sunset</a> <a href="http://t.co/YuKy2rcjyU">pic.twitter.com/YuKy2rcjyU</a></p>&mdash; US Dept of Interior (@Interior) <a href="https://twitter.com/Interior/status/463440424141459456">May 5, 2014</a></blockquote>',
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

    @mock.patch('msgvis.apps.api.serializers.DataTableSerializer')
    @mock.patch('msgvis.apps.datatable.models.DataTable')
    def test_get_datatable_api(self, DataTable, DataTableSerializer):
        # Fake dimensions and filters
        dimensions = [mock.Mock()]
        filters = mock.Mock()

        # Fake serialization
        serializer = DataTableSerializer.return_value
        serializer.is_valid.return_value = True
        serializer.validated_data = {
            'dataset': self.dataset.id,
            'dimensions': dimensions,
            'filters': filters,
        }

        # Fake the data table
        datatable = DataTable.return_value
        datatable.generate.return_value = mock.Mock()

        url = reverse('data-table')

        # Should be sending us back the same thing we sent in plus some extra
        expected_response = {
            'dataset': self.dataset.id,
            "dimensions": dimensions,
            "filters": filters,
            "result": datatable.generate.return_value,
        }

        # Fake serialized data
        serializer.data = {}

        request_data = {}
        response = self.client.post(url, request_data, format='json')

        # it should have rendered appropriately
        self.assertEquals(response.data, serializer.data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # It should have constructed a serializer using the request data
        # And also with the response data
        DataTableSerializer.assert_any_call(data=request_data)
        DataTableSerializer.assert_any_call(expected_response)

        # It should have checked for validity of input
        self.assertEquals(serializer.is_valid.call_count, 1)

        # It should have called the data table function
        DataTable.assert_called_once_with(*dimensions)
        # TODO: instead of using these ugly parameters, change them into mock
        datatable.generate.assert_called_once_with(self.dataset.id, filters, [], 30, None, None, None )

        # TODO: write tests for paging and searching
