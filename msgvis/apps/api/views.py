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
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from msgvis.apps.api import serializers
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.questions import models as questions_models
from msgvis.apps.datatable import models as datatable_models
import msgvis.apps.groups.models as groups_models
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
    with a new ``result`` field added. The result field
    includes a ``table``, which will be a list of objects.

    Each object in the table field represents a cell in a table or a dot
    (for scatterplot-type results). For every dimension in the dimensions
    list (from the request), the result object will include a property keyed
    to the name of the dimension and a value for that dimension. A ``value``
    field provides the requested summary statistic.

    The ``result`` field also includes a ``domains`` object, which
    defines the list of possible values within the selected data
    for each of the dimensions in the request.

    This is the most general output format for results, but later we may
    switch to a more compact format.

    **Request:** ``POST /api/table``

    **Format:** (request without ``result`` key)

    ::

        {
          "dataset": 1,
          "dimensions": ["time"],
          "filters": [
            {
              "dimension": "time",
              "min_time": "2015-02-25T00:23:53Z",
              "max_time": "2015-02-28T00:23:53Z"
            }
          ],
          "result": {
            "table": [
              {
                "value": 35,
                "time": "2015-02-25T00:23:53Z"
              },
              {
                "value": 35,
                "time": "2015-02-26T00:23:53Z"
              },
              {
                "value": 35,
                "time": "2015-02-27T00:23:53Z"
              },
              {
                "value": 35,
                "time": "2015-02-28T00:23:53Z"
              },
              "domains": {
                "time": [
                  "some_time_val",
                  "some_time_val",
                  "some_time_val",
                  "some_time_val"
                ]
              ],
              "domain_labels": {}
        }
    """

    def post(self, request, format=None):
        input = serializers.DataTableSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data

            dataset = data['dataset']
            dimensions = data['dimensions']
            filters = data.get('filters', [])
            exclude = data.get('exclude', [])
            search_key = data.get('search_key')
            mode = data.get('mode')
            groups = data.get('groups')

            page_size = 30
            page = None
            if data.get('page_size'):
                page_size = data.get('page_size')
                page_size = max(1, int(data.get('page_size')))
            if data.get('page'):
                page = max(1, int(data.get('page')))

            datatable = datatable_models.DataTable(*dimensions)
            if mode is not None:
                datatable.set_mode(mode)
            result = datatable.generate(dataset, filters, exclude, page_size, page, search_key, groups)

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
            "dataset": 1,
            "filters": [
                {
                    "dimension": "time",
                    "min_time": "2015-02-25T00:23:53Z",
                    "max_time": "2015-02-28T00:23:53Z"
                }
            ],
            "focus": [
                {
                    "dimension": "time",
                    "value": "2015-02-28T00:23:53Z"
                }
            ],
            "messages": [
                {
                    "id": 52,
                    "dataset": 1,
                    "text": "Some sort of thing or other",
                    "sender": {
                        "id": 2,
                        "dataset": 1
                        "original_id": 2568434,
                        "username": "my_name",
                        "full_name": "My Name"
                    },
                    "time": "2015-02-25T00:23:53Z"
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

class KeywordMessagesView(APIView):
    """
    Get some example messages matching the keyword.

    **Request:** ``POST /api/search``

    **Format:**: (request should not have ``messages`` key)

    ::

        {
            "dataset": 1,
            "keyword": "like",
            "messages": [
                {
                    "id": 52,
                    "dataset": 1,
                    "text": "Some sort of thing or other",
                    "sender": {
                        "id": 2,
                        "dataset": 1
                        "original_id": 2568434,
                        "username": "my_name",
                        "full_name": "My Name"
                    },
                    "time": "2015-02-25T00:23:53Z"
                }
            ]
        }
    """

    def post(self, request, format=None):
        input = serializers.KeywordMessageSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data

            dataset = data['dataset']

            inclusive_keywords = data.get('inclusive_keywords') or []
            exclusive_keywords = data.get('exclusive_keywords') or []
            #import pdb
            #pdb.set_trace()

            messages = dataset.get_advanced_search_results(inclusive_keywords, exclusive_keywords)

            # Just add the messages key to the response
            response_data = data
            response_data["messages"] = messages

            output = serializers.KeywordMessageSerializer(response_data, context={'request': request})
            return Response(output.data, status=status.HTTP_200_OK)

        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupView(APIView):
    """
    Get some example messages matching the keyword.

    **Request:** ``POST /api/group``

    **Format:**: (request should not have ``messages`` key)

    ::

        {
            "dataset": 1,
            "keyword": "like",
            "messages": [
                {
                    "id": 52,
                    "dataset": 1,
                    "text": "Some sort of thing or other",
                    "sender": {
                        "id": 2,
                        "dataset": 1
                        "original_id": 2568434,
                        "username": "my_name",
                        "full_name": "My Name"
                    },
                    "time": "2015-02-25T00:23:53Z"
                }
            ]
        }
    """


    def post(self, request, format=None):
        input = serializers.GroupSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data
            group = input.save()
            group.update_messages_in_group()


            # Just add the messages key to the response

            output = serializers.GroupListItemSerializer(group, context={'request': request})
            return Response(output.data, status=status.HTTP_200_OK)

        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        if request.query_params.get('dataset'):
            groups = groups_models.Group.objects.filter(dataset_id=int(request.query_params.get('dataset'))).all()
            output = serializers.GroupListSerializer(groups, many=True)
            return Response(output.data, status=status.HTTP_200_OK)
        elif request.query_params.get('group_id'):
            group = groups_models.Group.objects.get(id=int(request.query_params.get('group_id')))
            output = serializers.GroupListItemSerializer(group, context={'request': request})
            return Response(output.data, status=status.HTTP_200_OK)
        else:
            groups = groups_models.Group.objects.all()
            output = serializers.GroupListSerializer(groups, many=True)
            return Response(output.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        input = serializers.GroupSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data
            group = groups_models.Group.objects.get(id=data["id"])
            if data.get('name') is not None:
                group.name = data["name"]
                group.save()
            if data.get('inclusive_keywords'):
                group.add_inclusive_keywords(data.get('inclusive_keywords'))
            if data.get('exclusive_keywords'):
                group.add_exclusive_keywords(data.get('exclusive_keywords'))

            group.update_messages_in_group()
            output = serializers.GroupListItemSerializer(group, context={'request': request})
            return Response(output.data, status=status.HTTP_200_OK)

        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        if request.query_params.get('id'):
            group = groups_models.Group.objects.get(id=request.query_params.get('id'))
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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
