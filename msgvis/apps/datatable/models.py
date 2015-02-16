from django.db import models
from msgvis.apps.dimensions import registry

# Create your models here.
class DataTable(object):
    """
    This class knows how to calculate appropriate visualization data
    for a given pair of dimensions.
    """

    def __init__(self, primary_dimension, secondary_dimension=None):
        """
        Construct a DataTable for one or two dimensions.

        Dimensions may be string dimension keys or
        :class:`msgvis.apps.dimensions.models.BaseDimension` objects.
        """

        # Look up the dimensions if needed
        if isinstance(primary_dimension, basestring):
            primary_dimension = registry.get_dimension(primary_dimension)

        if secondary_dimension is not None and isinstance(secondary_dimension, basestring):
            secondary_dimension = registry.get_dimension(secondary_dimension)

        self.primary_dimension = primary_dimension
        self.secondary_dimension = secondary_dimension

    def render(self, messages):
        """
        Given a set of messages (already filtered as necessary),
        calculate the data table.

        The result is a list of dictionaries. Each
        dictionary contains a key for each dimension
        and a value key for the count.
        """
