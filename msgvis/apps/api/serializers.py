"""
This module defines serializers for the main API data objects:

.. autosummary::
    :nosignatures:

    DimensionSerializer
    FilterSerializer
    MessageSerializer
    QuestionSerializer

"""

from rest_framework import serializers

import msgvis.apps.corpus.models as corpus_models
import msgvis.apps.questions.models as questions_models
from msgvis.apps.dimensions import registry


# A simple string field that looks up dimensions on deserialization
class DimensionKeySerializer(serializers.CharField):
    def to_internal_value(self, data):
        return registry.get_dimension(data)

    def to_representation(self, instance):
        return instance.key


class DimensionSerializer(serializers.Serializer):
    """
    JSON representation of Dimensions for the API.

    Dimension objects describe the variables that users can select to
    visualize the dataset. An example is below:

    ::

        {
          "key": "time",
          "name": "Time",
          "description": "The time the message was sent",
        }
    """

    key = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    def to_internal_value(self, data):
        return registry.get_dimension(data['key'])


class FilterSerializer(serializers.Serializer):
    """
    Filters indicate a subset of the range of a specific dimension. Below is
    an array of three filter objects.

    ::

        [{
          "dimension": "time",
          "min_time": "2010-02-25T00:23:53Z",
          "max_time": "2010-02-28T00:23:53Z"
        },
        {
          "dimension": "words",
          "levels": [
            "cat",
            "dog",
            "alligator"
          ]
        },
        {
          "dimension": "reply_count",
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

    The 'value' field may also be used for exact matches.
    """

    dimension = DimensionKeySerializer()

    min = serializers.FloatField(required=False)
    max = serializers.FloatField(required=False)

    min_time = serializers.DateTimeField(required=False)
    max_time = serializers.DateTimeField(required=False)

    levels = serializers.ListSerializer(child=serializers.CharField(allow_null=True), required=False)

    value = serializers.CharField(required=False)


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = corpus_models.Person
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
        model = corpus_models.Message
        fields = ('id', 'dataset', 'text', 'sender', 'time')


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = questions_models.Article
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
          "dimensions": ["time", "author_name"]
        }

    The ``source`` object describes a research article reference where the
    question originated.

    The ``dimensions`` list indicates which dimensions the research question
    is associated with.
    """

    source = ArticleSerializer(read_only=True)
    dimensions = serializers.SlugRelatedField(many=True, read_only=True, slug_field='key', source="ordered_dimensions")

    class Meta:
        model = questions_models.Question
        fields = ('id', 'source', 'dimensions', 'text',)
        read_only_fields = fields


class ExampleMessageSerializer(serializers.Serializer):
    dataset = serializers.PrimaryKeyRelatedField(queryset=corpus_models.Dataset.objects.all())
    filters = serializers.ListField(child=FilterSerializer(), required=False)
    focus = serializers.ListField(child=FilterSerializer(), required=False)
    messages = serializers.ListField(child=MessageSerializer(), required=False, read_only=True)


class SampleQuestionSerializer(serializers.Serializer):
    dimensions = serializers.ListField(child=serializers.CharField(), required=False)
    questions = serializers.ListField(child=QuestionSerializer(), required=False, read_only=True)


class DataTableSerializer(serializers.Serializer):
    dataset = serializers.PrimaryKeyRelatedField(queryset=corpus_models.Dataset.objects.all())
    dimensions = serializers.ListField(child=DimensionKeySerializer())
    filters = serializers.ListField(child=FilterSerializer(), required=False)
    result = serializers.DictField(required=False, read_only=True)
