"""
Utility classes for calculating distributions over
various types of fields within the :class:`.Message` model.
"""

import math

from django.db import models
from django.conf import settings

# Note: Do not import models.Dimension in this file

QUANTITATIVE_DIMENSION_BINS = getattr(settings, 'QUANTITATIVE_DIMENSION_BINS', 50)


class CategoricalDistribution(object):
    """A distribution suitable for categorical variables."""

    def _get_grouping_expression(self, messages, field_name):
        """
        Returns a sql expression that will be used to group the messages.
        """
        return field_name

    def group_by(self, dataset, field_name):
        """
        Count the number of messages for each value of the dimension.
        If the dimension has no values available, an empty array is returned.

        ``field_name`` should be the field on the Message model we are grouping by.
        """

        messages = dataset.message_set.all()

        # Calculate a grouping variable
        grouping_expression = self._get_grouping_expression(messages, field_name)

        # Add it to our sql query (if it's just field_name, this is like an alias)
        messages = messages.extra(select={
            'value': grouping_expression
        })

        # Group by it
        messages = messages.values('value')

        # Count the messages in each group
        return messages.annotate(count=models.Count('id'))


class ForeignKeyDistribution(CategoricalDistribution):
    """Calculate distributions over a foreign key field"""

    def _get_grouping_expression(self, messages, field_name):
        """
        Returns a sql expression that will be used to group the messages.
        """
        return '%s_id' % field_name

    def group_by(self, dataset, field_name):
        """
        Count the number of messages for each value of the dimension.
        If the dimension has no values available, an empty array is returned.

        ``field_name`` should be the field on the Message model we are grouping by.
        """

        # Get the related field
        from msgvis.apps.corpus.models import Message

        field_descriptor = getattr(Message, field_name)
        related_model = field_descriptor.field.rel.to

        message_name = field_descriptor.field.related_query_name()

        query = related_model.objects.filter(**{
            '%s__dataset' % message_name: dataset
        })

        # Count the messages in each group
        return query.annotate(count=models.Count('%s__id' % message_name))


class QuantitativeDistribution(CategoricalDistribution):
    """A generic integer quantitative dimension distribution"""

    desired_bins = 20
    minimum_bin_size = 1
    grouping_expression_template = '{bin_size} * FLOOR(`{field_name}` / {bin_size})'

    def __init__(self, desired_bins=QUANTITATIVE_DIMENSION_BINS):
        super(QuantitativeDistribution, self).__init__()
        self.desired_bins = desired_bins

    def _get_bin_size(self, min_val, max_val):
        """
        Return a nice bin size given the min and max and the minimum bin count desired.
        The bin size returned will be at least ``minimum_bin_size``.
        """
        return max(self.minimum_bin_size,
                   math.floor(float(max_val - min_val) / self.desired_bins))

    def _get_range(self, messages, field_name):
        """
        Find a min and max for this field, as a tuple.
        If there isn't one, (None, None) is returned.
        """

        dim_range = messages.aggregate(min=models.Min(field_name),
                                       max=models.Max(field_name))

        if dim_range is None:
            return None, None

        return dim_range['min'], dim_range['max']

    def _get_grouping_expression(self, messages, field_name):
        """
        Returns an expression that bins the field by dividing
        by bin_size, flooring, and multiplying again.

        The bin size is calculated from the range of the dimension and
        a heuristic desired number of bins.
        """

        min_val, max_val = self._get_range(messages, field_name)

        if min_val is None:
            return []

        # Determine a bin size for this field
        best_bin_size = self._get_bin_size(min_val, max_val)

        if best_bin_size > self.minimum_bin_size:
            return self.grouping_expression_template.format(
                field_name=field_name,
                bin_size=best_bin_size
            )
        else:
            return super(QuantitativeDistribution, self)._get_grouping_expression(messages, field_name)


class TimeDistribution(QuantitativeDistribution):
    """
    Calculates distribution for time dimensions with
    human-friendly binning using heuristics from d3.
    """

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

    def _get_bin_size(self, min_time, max_time):
        """
        Determines a bin size for the time interval
        that supplies at least as many bins as minimum_bins,
        unless the time interval spans fewer than minimum_bins seconds.
        """

        extent = max_time - min_time
        bin_size = extent / self.desired_bins

        bin_size_seconds = bin_size.total_seconds()

        # Find the first human-friendly bin size that isn't bigger than bin_size_seconds
        best_bin_size = self.d3_time_scaleSteps[0]
        for step in self.d3_time_scaleSteps:
            if step < bin_size_seconds:
                best_bin_size = step
            else:
                break

        return best_bin_size


