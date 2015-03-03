"""Test that the registered dimensions can get their distributions"""

from django.test import TestCase

from datetime import timedelta
from django.utils import timezone as tz

from django.conf import settings

from msgvis.apps.dimensions import registry
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.base.tests import DistributionTestCaseMixins
from msgvis.apps.dimensions.models import QuantitativeDimension, TimeDimension


class TestQuantitativeBinning(TestCase):
    """Test the quantitative binning functions"""
    MIN_BIN_SIZE = 1
    DEFAULT_BINS = 50

    def setUp(self):
        self.dimension = QuantitativeDimension(
            key='fake',
            name='fake',
            description='fake',
            field_name='fake',
            default_bins=self.DEFAULT_BINS,
            min_bin_size=self.MIN_BIN_SIZE
        )

    def test_narrow_distribution(self):
        min_val = 0
        max_val = 11

        bin_size = self.dimension._get_bin_size(min_val, max_val, self.DEFAULT_BINS)

        self.assertEquals(bin_size, 1)
        self.assertEquals(self.dimension._bin_value(min_val, bin_size), 0)
        self.assertEquals(self.dimension._bin_value(max_val, bin_size), 11)


    def test_wide_distribution(self):
        min_val = 1
        max_val = 101

        bin_size = self.dimension._get_bin_size(min_val, max_val, 5)

        self.assertEquals(bin_size, 20)
        self.assertEquals(self.dimension._bin_value(min_val, bin_size), 0)
        self.assertEquals(self.dimension._bin_value(max_val, bin_size), 100)


class TestTimeBinning(TestCase):
    MIN_BIN_SIZE = 1
    DEFAULT_BINS = 50

    def setUp(self):
        self.base_time = tz.datetime(2012, 5, 2, 20, 10, 2, 0)
        if settings.USE_TZ:
            self.base_time = self.base_time.replace(tzinfo=tz.utc)

        self.dimension = TimeDimension(
            key='fake',
            name='fake',
            description='fake',
            field_name='fake',
            default_bins=self.DEFAULT_BINS,
            min_bin_size=self.MIN_BIN_SIZE
        )

    def test_narrow_distribution(self):
        min_val = self.base_time
        max_val = min_val + timedelta(minutes=30)

        bin_size = self.dimension._get_bin_size(min_val, max_val, 2000)

        self.assertEquals(bin_size, 1)
        self.assertEquals(self.dimension._bin_value(min_val, bin_size), min_val)
        self.assertEquals(self.dimension._bin_value(max_val, bin_size), max_val)


    def test_wide_distribution(self):
        min_val = self.base_time
        max_val = min_val + timedelta(days=4)

        # Remove the time parts
        day1 = min_val.replace(hour=0, minute=0, second=0, microsecond=0)
        day2 = min_val.replace(hour=0, minute=0, second=0, microsecond=0)

        bin_size = self.dimension._get_bin_size(min_val, max_val, 4)

        self.assertEquals(bin_size, 24 * 60 * 60)
        self.assertEquals(self.dimension._bin_value(min_val, bin_size), day1)
        self.assertEquals(self.dimension._bin_value(min_val, bin_size), day2)


    # These are just some extra time binning tests

    def run_time_bin_test(self, delta, desired_bins, expected_bin_size):
        """Run a generic time bin test."""
        t0 = self.base_time
        t1 = t0 + delta
        dimension = registry.get_dimension('time')
        self.assertEquals(dimension._get_bin_size(t0, t1, desired_bins), expected_bin_size)

    def test_time_bin_min_size(self):
        """Returns minimum bin size of 1 second."""
        self.run_time_bin_test(
            delta=tz.timedelta(seconds=4),
            desired_bins=10,
            expected_bin_size=1)

    def test_time_bin_max_size(self):
        """Returns a max bin size of 1 year."""
        self.run_time_bin_test(
            delta=tz.timedelta(days=10*365),
            desired_bins=5,
            expected_bin_size=31536e3)  # 1 year in seconds

    def test_time_bin_even_split(self):
        """Split evenly when the desired bins is perfect"""
        self.run_time_bin_test(
            delta=tz.timedelta(minutes=4),
            desired_bins=8,
            expected_bin_size=30,
            )

    def test_time_bin_at_least_desired(self):
        """Continues to deliver at least the desired bins"""
        self.run_time_bin_test(
            delta=tz.timedelta(minutes=4),
            desired_bins=7,
            expected_bin_size=30,
            )

    def test_time_bin_bumps_up(self):
        """If you ask for more bins, increases granularity"""
        self.run_time_bin_test(
            delta=tz.timedelta(minutes=4),
            desired_bins=9,
            expected_bin_size=30,
        ) # 4 minutes / 9 is 26.6 seconds, so it should go up

    def test_time_bin_special(self):
        self.run_time_bin_test(
            delta=tz.timedelta(minutes=4, seconds=11),
            desired_bins=50,
            expected_bin_size=5,
        )
