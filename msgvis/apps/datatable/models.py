from django.db import models

from msgvis.apps.base.models import MappedValuesQuerySet
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import registry


def find_messages(queryset):
    """If the given queryset is actually a :class:`.Dataset` model, get its messages queryset."""
    if isinstance(queryset, corpus_models.Dataset):
        queryset = queryset.message_set.all()
    return queryset


class DataTable(object):
    """
    This class knows how to calculate appropriate visualization data
    for a given pair of dimensions.
    """

    def __init__(self, primary_dimension, secondary_dimension=None):
        """
        Construct a DataTable for one or two dimensions.

        Dimensions may be string dimension keys or
        :class:`msgvis.apps.dimensions.models.CategoricalDimension` objects.

        :type primary_dimension: registry.models.CategoricalDimension
        :type secondary_dimension: registry.models.CategoricalDimension

        :return:
        """

        # Look up the dimensions if needed
        if isinstance(primary_dimension, basestring):
            primary_dimension = registry.get_dimension(primary_dimension)

        if secondary_dimension is not None and isinstance(secondary_dimension, basestring):
            secondary_dimension = registry.get_dimension(secondary_dimension)

        self.primary_dimension = primary_dimension
        self.secondary_dimension = secondary_dimension

    def render(self, queryset, desired_primary_bins=None, desired_secondary_bins=None):
        """
        Given a set of messages (already filtered as necessary),
        calculate the data table.

        Optionally, a number of primary and secondary bins may be given.

        The result is a list of dictionaries. Each
        dictionary contains a key for each dimension
        and a value key for the count.
        """

        # Type checking
        queryset = find_messages(queryset)

        if not self.secondary_dimension:
            # If there is only one dimension, we should be able to fall back
            # on that dimension's group_by() implementation.
            queryset = self.primary_dimension.group_by(queryset,
                                                       grouping_key=self.primary_dimension.key,
                                                       bins=desired_primary_bins)

            return queryset.annotate(value=models.Count('id'))

        else:
            # Now it gets nasty...
            primary_group = self.primary_dimension.get_grouping_expression(queryset,
                                                                           bins=desired_primary_bins)

            secondary_group = self.secondary_dimension.get_grouping_expression(queryset,
                                                                               bins=desired_secondary_bins)

            # Group the data
            queryset = queryset.values(primary_group, secondary_group)

            # Count the messages
            queryset = queryset.annotate(value=models.Count('id'))

            return MappedValuesQuerySet.create_from(queryset, {
                primary_group: self.primary_dimension.key,
                secondary_group: self.secondary_dimension.key,
            })

