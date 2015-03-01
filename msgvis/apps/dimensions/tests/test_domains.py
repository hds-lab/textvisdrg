"""Test that the registered dimensions can get their domains"""

from django.test import TestCase

from msgvis.apps.dimensions import registry
from msgvis.apps.base.tests import DistributionTestCaseMixins

class CategoricalDomainTest(DistributionTestCaseMixins, TestCase):

    def test_related_categorical_domain(self):
        """
        Checks that the domain of a categorical related model field,
        in this case Language, can be calculated correctly.
        """

        # Create some language labels
        language_ids = self.create_test_languages()
        language_distribution = self.get_distribution(language_ids)

        dataset = self.generate_messages_for_distribution(
            field_name='language_id',
            distribution=language_distribution,
        )

        dimension = registry.get_dimension('language')

        # Calculate the categorical distribution over the field name
        result = dimension.get_domain(dataset.message_set.all())

        # in descending order by frequency
        expected = ["fr", "jp", "en"]

        self.assertEquals(result, expected)

    def test_boolean_domain(self):
        dataset = self.create_empty_dataset()

        dimension = registry.get_dimension('contains_url')
        result = dimension.get_domain(dataset.message_set.all())
        result = list(result)
        result.sort()

        expected = [False, True]
        expected.sort()

        self.assertEquals(result, expected)
