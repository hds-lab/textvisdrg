from rest_framework.views import APIView, Response
from msgvis.api import serializers


class DataTableView(APIView):
    """
    Get a table of message counts or other statistics based on
    the current dimensions and filters.

    The request should post a JSON object containing a list
    of one or two dimension ids and a list of filters.
    A `measure` may also be specified in the request, but
    the default measure is message count.

    The response will be a JSON object that mimics the request body,
    but with a new `result` field added, which will be a list of objects.

    Each object in the result field represents a cell in a table
    or a dot (for scatterplot-type results). For every dimension
    in the dimensions list (from the request), the result object will include
    a property keyed to the name of the dimension and a value for that dimension.
    A `value` field provides the requested summary statistic.

    This is the most general output format for results,
    but later we may switch to a more compact format.
    """

    def post(self, request, format=None):
        return Response()


class ExampleMessagesView(APIView):
    """
    Get some example messages matching the current filters
    and a focus within the visualization.

    The request should include a list of dimension ids
    and active filters. It should also include a `focus` object
    that specifies values for one or both of the given dimensions,
    keyed by name.
    """
    def post(self, request, format=None):
        return Response()


class ResearchQuestionsView(APIView):
    """
    Get a list of research questions related to a selection
    of dimensions and filters.

    The request should include a list of dimension ids
    and active filters.

    The response will be a list of research questions.
    """
    def post(self, request, format=None):
        return Response()


class DimensionDistributionView(APIView):
    """
    In order to display helpful information for filtering,
    the distribution of a dimension may be queried using this API endpoint.

    The request should include a dimension `id` and an optional `query`
    for very large dimensions that support filtering the distribution.

    The response will include a `domain` property that is a list
    of values for the dimension with a message count at each value.
    """
    def post(self, request, format=None):
        return Response()


class FilterSummaryView(APIView):
    """
    When a filter is being used, it is useful to know information
    about how the filter behaves on the dataset.

    The request should include a filter object.

    The response will add a `summary` object
    that includes some statistics about the filter.
    """
    def post(self, request, format=None):
        return Response()



