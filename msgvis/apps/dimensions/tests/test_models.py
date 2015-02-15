from django.test import TestCase
import mock

from msgvis.apps.dimensions import models

class DimensionDistributionTest(TestCase):
    def test_can_get_distribution(self):
        """Just check that the Dimension.get_distribution method runs"""

        contains_mention = models.CategoricalDimension(
            key='contains_url',
            name='Contains a url',
            description='Contains a url',
            field_name='contains_url',
        )

        dataset = mock.Mock()
        distribution = mock.Mock()
        with mock.patch.object(contains_mention, 'distribution', distribution):
            result = contains_mention.get_distribution(dataset)

        distribution.group_by.assert_called_once_with(dataset, contains_mention.field_name)



