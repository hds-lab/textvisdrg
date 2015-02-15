"""
Utility classes for calculating distributions over
various types of fields within the :class:`.Message` model.
"""

import math

from django.db import models
from django.conf import settings

from msgvis.apps.corpus.models import Message

# Note: Do not import models.Dimension in this file

QUANTITATIVE_DIMENSION_BINS = getattr(settings, 'QUANTITATIVE_DIMENSION_BINS', 50)


class BaseDistribution(object):
    field_name = None

    def group_by(self, dataset, field_name=None):
        """
        Count the number of messages for each value of the dimension.
        If the dimension has no values available, an empty array is returned.

        ``field_name`` should be the field on the Message model we are grouping by.

        The result will be a queryset or list, containing either
        Model objects (if the field is a ForeignKey or ManyToMany field)
        augmented by a 'count' attribute,
        or dictionaries with value and count keys if the field type is simple.
        """
        raise NotImplementedError("Silly, you can't use a BaseDistribution")

    def _get_base_set(self, dataset):
        return dataset.message_set.all()


class CategoricalDistribution(BaseDistribution):
    """A distribution suitable for simple categorical variables."""

    def group_by(self, dataset, field_name=None):
        if field_name is None:
            field_name = self.field_name

        items = self._get_base_set(dataset)

        # Group by the field
        items = items.values(field_name)

        # Count the messages in each group
        grouped = items.annotate(count=models.Count('id'))

        # Now we have to normalize the output though
        # so that it uses a 'value' key.
        return [{
                    'value': g[field_name],
                    'count': g['count'],
                } for g in grouped]


class ForeignKeyDistribution(BaseDistribution):
    """Calculate distributions over a foreign key field"""

    def group_by(self, dataset, field_name=None):
        """
        Count the number of messages for each value of the dimension.
        If the dimension has no values available, an empty array is returned.

        ``field_name`` should be the field on the Message model we are grouping by.
        """
        if field_name is None:
            field_name = self.field_name

        # Get the related field
        field_descriptor = getattr(Message, field_name)
        related_model = field_descriptor.field.rel.to

        message_name = field_descriptor.field.related_query_name()

        query = related_model.objects.filter(**{
            '%s__dataset' % message_name: dataset
        })

        # Count the messages in each group
        return query.annotate(count=models.Count('%s__id' % message_name))


class BinnedResultSet(list):
    """A class for storing binned results with metadata."""

    def __init__(self, items, bin_size, min_val, max_val):
        super(BinnedResultSet, self).__init__(items)
        self.bin_size = bin_size
        self.min_val = min_val
        self.max_val = max_val


class QuantitativeDistribution(BaseDistribution):
    """A generic integer quantitative dimension distribution"""

    desired_bins = 20
    minimum_bin_size = 1
    grouping_expressions = {
        'mysql': '{bin_size} * FLOOR(`{field_name}` / {bin_size})',
        'sqlite': '{bin_size} * CAST(`{field_name}` / {bin_size} AS INTEGER)',
    }

    def __init__(self, desired_bins=QUANTITATIVE_DIMENSION_BINS):
        super(QuantitativeDistribution, self).__init__()
        self.desired_bins = desired_bins

    def _get_range(self, items, field_name):
        """
        Find a min and max for this field, as a tuple.
        If there isn't one, (None, None) is returned.
        """

        dim_range = items.aggregate(min=models.Min(field_name),
                                    max=models.Max(field_name))

        if dim_range is None:
            return None, None

        return dim_range['min'], dim_range['max']

    def _get_bin_size(self, min_val, max_val):
        """
        Return a nice bin size with the min and max as a tuple.
        The bin size returned will be at least ``minimum_bin_size``.
        """

        bin_size = max(self.minimum_bin_size,
                       math.floor(float(max_val - min_val) / self.desired_bins))

        return bin_size

    def _render_grouping_expression(self, field_name, bin_size):
        from django.db import connection

        return self.grouping_expressions[connection.vendor].format(
            field_name=field_name,
            bin_size=bin_size
        )

    def _add_grouping_value(self, items, bin_size, field_name, select_name='value'):
        """
        Calculate a value that bins the field by dividing
        by bin_size, flooring, and multiplying again.

        The bin size is calculated from the range of the dimension and
        a heuristic desired number of bins.
        """

        # Determine a bin size for this field
        if bin_size > self.minimum_bin_size:
            grouping = self._render_grouping_expression(field_name, bin_size)
        else:
            # No need for binning
            grouping = field_name

        # Add it to our sql query (if it's just field_name, this is like an alias)

        # We can's just use items.extra() because of a bug in Django < 1.8.
        # Sqlite uses %s to convert to unix timestamps.
        # Django's QuerySet.extra() thinks that any %s needs to have a
        # param so if we don't provide one, it errors.
        # If we do provide one, the Sqlite engine complains because it knows better.
        items = items._clone()
        items.query.extra.update({
            select_name: (grouping, ())
        })

        return items

    def _annotate(self, items):
        return items.annotate(count=models.Count('id'))

    def group_by(self, dataset, field_name=None):
        if field_name is None:
            field_name = self.field_name

        items = self._get_base_set(dataset)

        # Get the min and max
        min_val, max_val = self._get_range(items, field_name)
        if min_val is None:
            return []

        # Get a good bin size
        bin_size = self._get_bin_size(min_val, max_val)

        # Calculate a grouping variable
        items = self._add_grouping_value(items, bin_size, field_name)

        # Group by it
        items = items.values('value')

        # Count the messages in each group
        result = self._annotate(items)

        return BinnedResultSet(result, bin_size, min_val, max_val)


class PersonQuantitativeDistribution(QuantitativeDistribution):
    """A distribution of a quantitative variable of a related Person"""
    person_field = 'sender'

    def _get_base_set(self, dataset):
        return dataset.person_set.all()

    def _annotate(self, items):
        return items.annotate(count=models.Count('message'))


class TimeDistribution(QuantitativeDistribution):
    """
    Calculates distribution for time dimensions with
    human-friendly binning using heuristics from d3.
    """
    field_name = 'time'

    # Convert to unix timestamp. Divide by bin size. Floor. Multiply by bin size. Convert to datetime.
    grouping_expressions = {
        'mysql': r"FROM_UNIXTIME({bin_size} * FLOOR(UNIX_TIMESTAMP(`{field_name}`) / {bin_size}))",
        'sqlite': r"DATETIME({bin_size} * CAST(STRFTIME('%%s', `{field_name}`) / {bin_size} AS INTEGER), 'unixepoch')"
    }

    # A range of human-friendly time bin sizes
    # https://github.com/mbostock/d3/blob/master/src/time/scale.js
    # NOTE: these are in milliseconds! (JS uses millis)
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

        bin_size_millis = 1000 * bin_size_seconds

        # Find the first human-friendly bin size that isn't bigger than bin_size_seconds
        best_bin_millis = self.d3_time_scaleSteps[0]
        for step in self.d3_time_scaleSteps:
            if step <= bin_size_millis:
                best_bin_millis = step
            else:
                break

        return best_bin_millis / 1000


