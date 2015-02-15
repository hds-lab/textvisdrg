from django.test import TestCase

from msgvis.apps.dimensions import models, registry


class DimensionRegistryTest(TestCase):
    """Test the dimension registry"""

    def test_registry_contains_dimension(self):
        """The registry should have some dimensions"""
        time = registry.get_dimension('time')
        self.assertIsNotNone(time)
        self.assertIsInstance(time, models.TimeDimension)

    def test_registry_size(self):
        """The number of dimensions registered should be 24"""
        self.assertEquals(len(registry.get_dimension_ids()), 24)

    def test_registry_rejects_unknown_keys(self):
        """Trying to get a dimension for a nonexistent key raises an exeption"""
        with self.assertRaises(KeyError):
            registry.get_dimension('made_up_dimension_key')


