from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from rest_framework import status

from msgvis.apps.corpus import models as corpus_models
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
