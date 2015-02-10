"""
This module defines serializers for the main API data objects:

.. autosummary::
    :nosignatures:

    DimensionSerializer
    MessageSerializer
    QuestionSerializer
    FilterSerializer

"""

from rest_framework import serializers

from msgvis.apps.corpus.models import Message, Person
from msgvis.apps.questions.models import Question, Article
from msgvis.apps.dimensions.models import Dimension


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ('id', 'dataset', 'original_id', 'username', 'full_name',)


class MessageSerializer(serializers.ModelSerializer):
    """
    JSON representation of :class:`.Message`
    objects for the API.

    Messages are provided in a simple format that is useful for displaying
    examples:

    ::

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

    Additional fields may be added later.
    """

    sender = PersonSerializer()

    class Meta:
        model = Message
        fields = ('id', 'dataset', 'text', 'sender', 'time')


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'authors', 'link', 'title', 'year', 'venue',)


class QuestionSerializer(serializers.ModelSerializer):
    """
    JSON representation of a :class:`.Question`
    object for the API.

    Research questions extracted from papers are given in the following
    format:

    ::

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
          "dimensions": [4, 5]
        }

    The ``source`` object describes a research article reference where the
    question originated.

    The ``dimensions`` list indicates which dimensions the research question
    is associated with.
    """

    source = ArticleSerializer()

    class Meta:
        model = Question
        fields = ('id', 'source', 'dimensions', 'text',)


class DimensionSerializer(serializers.ModelSerializer):
    """
    JSON representation of :class:`.Dimension`
    objects for the API.

    Dimension objects describe the variables that users can select to
    visualize the dataset. An example is below:

    ::

        {
          "id": 5,
          "name": "time",
          "description": "the time the message was sent",
          "scope": "open",
          "type": "quantitative",
        }
    """

    class Meta:
        model = Dimension
        fields = ('id', 'name', 'description', 'scope', 'type')


class FilterSerializer(serializers.Serializer):
    """
    Filters indicate a subset of the range of a specific dimension. Below is
    an array of three filter objects.

    ::

        [{
          "dimension": 5,
          "min_time": "2010-02-25T00:23:53Z",
          "max_time": "2010-02-30T00:23:53Z"
        },
        {
          "dimension": 2,
          "include": [
            "cat",
            "dog",
            "alligator"
          ]
        },
        {
          "dimension": 6,
          "max": 100
        }]

    Although every filter has a ``dimension`` field, the specific properties
    vary depending on the type of the dimension and the kind of filter.

    At this time, there are three types of filters:

    -  Quantitative dimensions can be filtered using one or both of the
       ``min`` and ``max`` properties (inclusive).
    -  The time dimension can be filtered using one or both of the ``min_time``
       and ``max_time`` properties (inclusive).
    -  Categorical dimensions can be filtered by specifying an ``include``
       list. All other items are assumed to be excluded.
    """

    dimension = serializers.PrimaryKeyRelatedField(queryset=Dimension.objects.all())

    min = serializers.FloatField(required=False)
    max = serializers.FloatField(required=False)

    min_time = serializers.DateTimeField(required=False)
    max_time = serializers.DateTimeField(required=False)

    include = serializers.ListSerializer(child=serializers.CharField(), required=False)
