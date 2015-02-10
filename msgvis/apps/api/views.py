"""
The view classes below define the API endpoints.

+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| Endpoint                                                        | Url             | Purpose                                         |
+=================================================================+=================+=================================================+
| :class:`Get Data Table <DataTableView>`                         | /api/table      | Get table of counts based on dimensions/filters |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| :class:`Get Example Messages <ExampleMessagesView>`             | /api/messages   | Get example messages for slice of data          |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| :class:`Get Research Questions <ResearchQuestionsView>`         | /api/questions  | Get RQs related to dimensions/filters           |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| :class:`Get Dimension Distribution <DimensionDistributionView>` | /api/dimension  | Get distribution of a dimension                 |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| :class:`Get Filter Summary <FilterSummaryView>`                 | /api/filter     | Get info about behavior of filter               |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| Message Context                                                 | /api/context    | Get context for a message                       |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| Snapshots                                                       | /api/snapshots  | Save a visualization snapshot                   |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
"""

from rest_framework.views import APIView, Response
from django.core.urlresolvers import NoReverseMatch
from rest_framework.reverse import reverse

from rest_framework.compat import get_resolver_match, OrderedDict


class DataTableView(APIView):
    """
    Get a table of message counts or other statistics based on the current
    dimensions and filters.

    The request should post a JSON object containing a list of one or two
    dimension ids and a list of filters. A ``measure`` may also be specified
    in the request, but the default measure is message count.

    The response will be a JSON object that mimics the request body, but
    with a new ``result`` field added, which will be a list of objects.

    Each object in the result field represents a cell in a table or a dot
    (for scatterplot-type results). For every dimension in the dimensions
    list (from the request), the result object will include a property keyed
    to the name of the dimension and a value for that dimension. A ``value``
    field provides the requested summary statistic.

    This is the most general output format for results, but later we may
    switch to a more compact format.

    **Request:** ``POST /api/table``

    **Example Request Body:**

    ::

        {
          "dimensions": [5, 8],
          "filters": [
            {
              "dimension": 5,
              "min": "2010-02-25T00:23:53Z",
              "max": "2010-02-30T00:23:53Z"
            }
          ],
          "measure": {
            "statistic": "message",
            "aggregation": "count"
          }
        }

    **Example Response Body:**

    ::

        {
          "dimensions": [5, 8],
          "filters": [
            {
              "dimension": 5,
              "min": "2010-02-25T00:23:53Z",
              "max": "2010-02-30T00:23:53Z"
            }
          ],
          "result": [
            {
              "value": 35,
              "time": "2010-02-25T00:23:53Z"
            },
            {
              "value": 35,
              "time": "2010-02-26T00:23:53Z"
            },
            {
              "value": 35,
              "time": "2010-02-27T00:23:53Z"
            },
            {
              "value": 35,
              "time": "2010-02-28T00:23:53Z"
            }
          ]
        }
    """

    def post(self, request, format=None):
        return Response()


class ExampleMessagesView(APIView):
    """
    Get some example messages matching the current filters and a focus
    within the visualization.

    The request should include a list of dimension ids and active filters.
    It should also include a ``focus`` object that specifies values for one
    or both of the given dimensions, keyed by name.

    The response will be a list of `message objects <#messages>`_.

    **Request:** ``POST /api/messages``

    **Example Request Body:**

    ::

        {
          "dimensions": [5, 8],
          "filters": [
            {
              "dimension": 5,
              "min": "2010-02-25T00:23:53Z",
              "max": "2010-02-30T00:23:53Z"
            }
          ],
          "focus": {
            "time": "2010-02-30T00:23:53Z"
          }
        }
    """

    def post(self, request, format=None):
        return Response()


class ResearchQuestionsView(APIView):
    """
    Get a list of research questions related to a selection of dimensions and filters.
    The request should include a list of :class:`Dimension` ids and filter specifications.

    The response will be a list of Research :class:`Questions`.

    **Request:** ``POST /api/questions``

    **Example Request Body:**

    ::

        {
          "dimensions": [5, 8],
          "filters": [
            {
              "dimension": 5,
              "min": "2010-02-25T00:23:53Z",
              "max": "2010-02-30T00:23:53Z"
            }
          ]
        }
    """

    def post(self, request, format=None):
        return Response()


class DimensionDistributionView(APIView):
    """
    In order to display helpful information for filtering, the distribution
    of a dimension may be queried using this API endpoint.

    The request should include a dimension ``id`` and an optional ``query``
    for very large dimensions that support filtering the distribution.

    The response will include a ``domain`` property that is a list of values
    for the dimension with a message count at each value.

    **Request:** ``POST /api/dimension``

    **Example Request Body:**

    ::

        {
          "id": 7,
          "query": "cat"
        }

    **Example Response:**

    ::

        {
          "id": 7,
          "query": "cat",
          "domain": [
            {
              "count": 5000,
              "value": "cat"
            },
            {
              "count": 1000,
              "value": "catch"
            },
            {
              "count": 500,
              "value": "cathedral"
            },
            {
              "count": 50,
              "value": "cataleptic"
            }
          ]
        }
    """

    def post(self, request, format=None):
        return Response()


class FilterSummaryView(APIView):
    """
    When a filter is being used, it is useful to know information about how
    the filter behaves on the dataset.
    The request should include a `filter object <#filters>`_.

    The response will add a ``summary`` object that includes some statistics
    about the filter.

    **Request:** ``POST /api/filter``

    **Example Request Body:**

    ::

        {
          "dimension": 5,
          "min": "2010-02-25T00:23:53Z",
          "max": "2010-02-30T00:23:53Z"
        }

    **Example Response:**

    ::

        {
          "dimension": 5,
          "min": "2010-02-25T00:23:53Z",
          "max": "2010-02-30T00:23:53Z",
          "summary": {
            "included": 502343
          }
        }

    """

    def post(self, request, format=None):
        return Response()


class APIRoot(APIView):
    """
    The Text Visualization DRG Root API View.
    """
    root_urls = {}

    def get(self, request, *args, **kwargs):
        ret = OrderedDict()
        namespace = get_resolver_match(request).namespace
        for key, urlconf in self.root_urls.iteritems():
            url_name = urlconf.name
            if namespace:
                url_name = namespace + ':' + url_name
            try:
                ret[key] = reverse(
                    url_name,
                    request=request,
                    format=kwargs.get('format', None)
                )
                print ret[key]
            except NoReverseMatch:
                # Don't bail out if eg. no list routes exist, only detail routes.
                continue

        return Response(ret)
