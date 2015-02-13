"""
Utility classes for calculating distributions over
various types of fields within the :class:`.Message` model.
"""

import math

from django.db import models
from django.conf import settings

# Note: Do not import models.Dimension in this file


quantitative_dimension_bins = getattr(settings, 'QUANTITATIVE_DIMENSION_BINS', 50)


class CategoricalDistribution(object):
    """A distribution suitable for categorical variables."""

    def __init__(self, field_name):
        """field_name should be a field on the Message model."""
        self.field_name = field_name

    def _get_grouping_expression(self, messages):
        """
        Returns a sql expression that will be used to group the messages.
        """
        return self.field_name

    def group_by(self, messages):
        """
        Count the number of messages for each value of the dimension.
        If the dimension has no values available, an empty array is returned.
        """

        # Calculate a grouping variable
        grouping_expression = self._get_grouping_expression(messages)

        # Add it to our sql query (if it's just field_name, this is like an alias)
        messages = messages.extra(select={
            'value': grouping_expression
        })

        # Group by it
        messages = messages.values('value')

        # Count the messages in each group
        return messages.annotate(count=models.Count('id'))


class QuantitativeDistribution(CategoricalDistribution):
    """A generic integer quantitative dimension distribution"""

    grouping_expression_template = '{bin_size} * FLOOR(`{field_name}` / {bin_size})'

    def _get_bin_size(self, min_val, max_val, minimum_bins):
        """
        Return a nice bin size given the min and max and the minimum bin count desired.
        The bin size returned will be at least 1.
        """
        return max(1, math.floor(float(max_val - min_val) / minimum_bins))

    def _get_range(self, messages):
        """
        Find a min and max for this field, as a tuple.
        If there isn't one, (None, None) is returned.
        """

        dim_range = messages.aggregate(min=models.Min(self.field_name),
                                       max=models.Max(self.field_name))

        if dim_range is None:
            return None, None

        return dim_range['min'], dim_range['max']

    def _get_grouping_expression(self, messages):
        """
        Returns an expression that bins the field by dividing
        by bin_size, flooring, and multiplying again.

        The bin size is calculated from the range of the dimension and
        a heuristic desired number of bins.
        """

        min_val, max_val = self._get_range(messages)

        if min_val is None:
            return []

        # Determine a bin size for this field
        best_bin_size = self._get_bin_size(min_val, max_val, quantitative_dimension_bins)

        return self.grouping_expression_template.format(
            field_name=self.field_name,
            bin_size=best_bin_size
        )


class TimeDistribution(QuantitativeDistribution):
    # Convert to unix timestamp. Divide by bin size. Floor. Multiply by bin size. Convert to datetime.
    grouping_expression_template = 'FROM_UNIXTIME({bin_size} * FLOOR(UNIX_TIMESTAMP(`{field_name}`) / {bin_size}))'

    # A range of human-friendly time bin sizes
    # https://github.com/mbostock/d3/blob/master/src/time/scale.js
    d3_time_scaleSteps = [
        1e3,  # 1-second
        5e3,  # 5-second
        15e3,  # 15-second
        3e4,  # 30-second
        6e4,  # 1-minute
        3e5,  # 5-minute
        9e5,  # 15-minute
        18e5,  # 30-minute
        36e5,  # 1-hour
        108e5,  # 3-hour
        216e5,  # 6-hour
        432e5,  # 12-hour
        864e5,  # 1-day
        1728e5,  # 2-day
        6048e5,  # 1-week
        2592e6,  # 1-month
        7776e6,  # 3-month
        31536e6  # 1-year
    ]

    def _get_bin_size(self, min_time, max_time, minimum_bins):
        """
        Determines a bin size for the time interval
        that supplies at least as many bins as minimum_bins,
        unless the time interval spans fewer than minimum_bins seconds.
        """

        extent = max_time - min_time
        bin_size = extent / minimum_bins

        bin_size_seconds = bin_size.total_seconds()

        # Find the first human-friendly bin size that isn't bigger than bin_size_seconds
        best_bin_size = self.d3_time_scaleSteps[0]
        for step in self.d3_time_scaleSteps:
            if step < bin_size_seconds:
                best_bin_size = step
            else:
                break

        return best_bin_size


