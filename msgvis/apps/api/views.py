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
| Message Context                                                 | /api/context    | Get context for a message                       |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
| Snapshots                                                       | /api/snapshots  | Save a visualization snapshot                   |
+-----------------------------------------------------------------+-----------------+-------------------------------------------------+
"""

from rest_framework import status
from rest_framework.views import APIView, Response
from django.core.urlresolvers import NoReverseMatch
from rest_framework.reverse import reverse
from rest_framework.compat import get_resolver_match, OrderedDict

from msgvis.apps.api import serializers
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.questions import models as questions_models
from msgvis.apps.datatable import models as datatable_models
import logging

logger = logging.getLogger(__name__)


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

    **Format:** (request without ``result`` key)

    ::

        {
          "dataset": 2,
          "dimensions": ["time"],
          "filters": [
            {
              "dimension": "time",
              "min": "2010-02-25T00:23:53Z",
              "max": "2010-02-28T00:23:53Z"
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
        input = serializers.DataTableSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data

            dimensions = data['dimensions']
            filters = data.get('filters', [])

            queryset = corpus_models.Message.objects.all()

            # Filter the data
            for filter in filters:
                dimension = filter['dimension']
                queryset = dimension.filter(queryset, filter)

            # Render a table
            table = datatable_models.DataTable(*dimensions)
            result = table.render(queryset)

            # Just add the result key
            response_data = data
            response_data['result'] = result

            output = serializers.DataTableSerializer(response_data)
            return Response(output.data, status=status.HTTP_200_OK)

        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)


class ExampleMessagesView(APIView):
    """
    Get some example messages matching the current filters and a focus
    within the visualization.

    **Request:** ``POST /api/messages``

    **Format:**: (request should not have ``messages`` key)

    ::

        {
            "dataset": 2,
            "filters": [
                {
                    "dimension": "time",
                    "min_time": "2010-02-25T00:23:53Z",
                    "max_time": "2010-02-28T00:23:53Z"
                }
            ],
            "focus": [
                {
                    "dimension": "time",
                    "value": "2010-02-28T00:23:53Z"
                }
            ],
            "messages": [
                {
                    "id": 52,
                    "dataset": 2,
                    "text": "Some sort of thing or other",
                    "sender": {
                        "id": 2,
                        "dataset": 1
                        "original_id": 2568434,
                        "username": "my_name",
                        "full_name": "My Name"
                    },
                    "time": "2010-02-25T00:23:53Z"
                }
            ]
        }
    """

    def post(self, request, format=None):
        input = serializers.ExampleMessageSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data

            dataset = data['dataset']

            filters = data['filters']
            focus = data.get('focus', [])

            example_messages = dataset.get_example_messages(filters + focus)

            # Just add the messages key to the response
            response_data = data
            response_data["messages"] = example_messages

            output = serializers.ExampleMessageSerializer(response_data)
            return Response(output.data, status=status.HTTP_200_OK)

        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)


class ResearchQuestionsView(APIView):
    """
    Get a list of research questions related to a selection of dimensions and filters.

    **Request:** ``POST /api/questions``

    **Format:** (request without ``questions`` key)

    ::

        {
            "dimensions": ["time", "hashtags"],
            "questions": [
                {
                  "id": 5,
                  "text": "What is your name?",
                  "source": {
                    "id": 13,
                    "authors": "Thingummy & Bob",
                    "link": "http://ijn.com/3453295",
                    "title": "Names and such",
                    "year": "2001",
                    "venue": "International Journal of Names"
                  },
                  "dimensions": ["time", "author_name"]
                }
            ]
        }
    """

    def post(self, request, format=None):
        input = serializers.SampleQuestionSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data

            dimension_list = data["dimensions"]
            questions = questions_models.Question.get_sample_questions(*dimension_list)

            response_data = {
                "dimensions": dimension_list,
                "questions": questions
            }

            output = serializers.SampleQuestionSerializer(response_data)
            return Response(output.data, status=status.HTTP_200_OK)

        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)


class DimensionDistributionView(APIView):
    """
    In order to display helpful information for filtering, the distribution
    of a dimension may be queried using this API endpoint.

    **Request:** ``POST /api/dimension``

    **Format:** (requests should not include the ``distribution`` key)

    ::

        {
          "dataset": 2,
          "dimension": "time",
          "distribution": [
            {
              "count": 5000,
              "value": "some_time"
            },
            {
              "count": 1000,
              "value": "some_time"
            },
            {
              "count": 500,
              "value": "some_time"
            },
            {
              "count": 50,
              "value": "some_time"
            }
          ]
        }
    """

    def post(self, request, format=None):
        input = serializers.DimensionDistributionSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data

            dimension = data['dimension']
            dataset = data['dataset']

            response_data = {
                'dimension': dimension,
                'dataset': dataset,
                'distribution': dimension.get_distribution(dataset),
            }

            output = serializers.DimensionDistributionSerializer(response_data)
            return Response(output.data, status=status.HTTP_200_OK)

        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)


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
