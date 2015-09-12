"""
This module defines serializers for the main API data objects:

.. autosummary::
    :nosignatures:

    DimensionSerializer
    FilterSerializer
    MessageSerializer
    QuestionSerializer

"""
from django.core.paginator import Paginator

from rest_framework import serializers, pagination

import msgvis.apps.corpus.models as corpus_models
import msgvis.apps.questions.models as questions_models
import msgvis.apps.enhance.models as enhance_models
import msgvis.apps.groups.models as groups_models
from msgvis.apps.dimensions import registry
from django.contrib.auth.models import User

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

    levels = serializers.ListSerializer(child=serializers.CharField(allow_null=True, allow_blank=True), required=False)

    value = serializers.CharField(allow_null=True, allow_blank=True, required=False)


class PersonSerializer(serializers.ModelSerializer):
    profile_image_local_name = serializers.CharField()
    class Meta:
        model = corpus_models.Person
        fields = ('id', 'dataset', 'original_id', 'username', 'full_name', 'profile_image_local_name', )


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
    embedded_html = serializers.CharField()
    media_url = serializers.CharField()

    class Meta:
        model = corpus_models.Message
        fields = ('id', 'dataset', 'text', 'sender', 'time', 'original_id', 'embedded_html', 'media_url', )


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

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = enhance_models.Word

    def to_representation(self, instance):
        return instance.text

class MessageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = corpus_models.MessageType

    def to_representation(self, instance):
        return instance.name

class ExampleMessageSerializer(serializers.Serializer):
    dataset = serializers.PrimaryKeyRelatedField(queryset=corpus_models.Dataset.objects.all())
    filters = serializers.ListField(child=FilterSerializer(), required=False)
    focus = serializers.ListField(child=FilterSerializer(), required=False)
    #messages = serializers.ListField(child=MessageSerializer(), required=False, read_only=True)
    groups = serializers.ListField(child=serializers.IntegerField(), required=False)
    messages = serializers.SerializerMethodField('paginated_messages')
    def paginated_messages(self, obj):
        request = self.context.get('request')
        messages_per_page = 10
        page = 1

        if request and request.query_params.get('page'):
            page = request.query_params.get('page')
        if request and request.query_params.get('messages_per_page'):
            messages_per_page = request.query_params.get('messages_per_page')

        paginator = Paginator(obj["messages"][:], messages_per_page)
        messages = paginator.page(page)

        serializer = PaginatedMessageSerializer(messages)
        return serializer.data


class KeywordMessageSerializer(serializers.Serializer):
    dataset = serializers.PrimaryKeyRelatedField(queryset=corpus_models.Dataset.objects.all())
    keywords = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    messages = serializers.SerializerMethodField('paginated_messages')
    types_list = serializers.ListField(child=serializers.CharField(), required=False)

    def paginated_messages(self, obj):
        request = self.context.get('request')
        messages_per_page = 10
        page = 1

        if request and request.query_params.get('page'):
            page = request.query_params.get('page')
        if request and request.query_params.get('messages_per_page'):
            messages_per_page = request.query_params.get('messages_per_page')

        paginator = Paginator(obj["messages"].all(), messages_per_page)
        messages = paginator.page(page)

        serializer = PaginatedMessageSerializer(messages)
        return serializer.data


class KeywordListSerializer(serializers.Serializer):
    dataset = serializers.IntegerField(required=True)
    q = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    keywords = serializers.ListField(child=serializers.CharField(), required=False)


class PaginatedMessageSerializer(pagination.PaginationSerializer):
    class Meta:
        object_serializer_class = MessageSerializer


class GroupSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField('paginated_messages', required=False)
    message_count = serializers.IntegerField(required=False)
    include_types = MessageTypeSerializer(many=True, required=False)
    types_list = serializers.ListField(child=serializers.CharField(), required=False)
    order = serializers.IntegerField(required=False, read_only=True)
    is_search_record = serializers.BooleanField(default=False)

    class Meta:
        model = groups_models.Group
        fields = ('id', 'owner', 'order', 'dataset', 'name', 'keywords', 'messages', 'message_count', 'include_types', 'types_list', 'is_search_record', )
        read_only_fields = ('owner', 'order', )

    def paginated_messages(self, obj):
        if self.context and self.context.get('show_message'):
            paginator = Paginator(obj.messages.all(), 10)
            page = 1
            request = self.context.get('request')

            if request and request.query_params.get('page'):
                page = request.query_params.get('page')
            messages = paginator.page(page)

            serializer = PaginatedMessageSerializer(messages)
            return serializer.data
        else:
            return None

    def create(self, validated_data):
        group = groups_models.Group.objects.create(dataset=validated_data["dataset"],
                                                   name=validated_data["name"])
        if validated_data.get('keywords'):
            group.keywords = validated_data.get('keywords')
            group.save()
        if validated_data.get('types_list'):
            include_types = [corpus_models.MessageType.objects.get(name=x) for x in validated_data.get('types_list')]
            group.include_types = include_types
        else:
            include_types = corpus_models.MessageType.objects.filter(id > 0).all()
            group.include_types = include_types


        return group


class SampleQuestionSerializer(serializers.Serializer):
    dimensions = serializers.ListField(child=serializers.CharField(), required=False)
    questions = serializers.ListField(child=QuestionSerializer(), required=False, read_only=True)


class DataTableSerializer(serializers.Serializer):
    dataset = serializers.PrimaryKeyRelatedField(queryset=corpus_models.Dataset.objects.all())
    dimensions = serializers.ListField(child=DimensionKeySerializer())
    filters = serializers.ListField(child=FilterSerializer(), required=False)
    exclude = serializers.ListField(child=FilterSerializer(), required=False)
    result = serializers.DictField(required=False, read_only=True)
    page_size = serializers.IntegerField(required=False)
    page = serializers.IntegerField(required=False)
    search_key = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    mode = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    groups = serializers.ListField(child=serializers.IntegerField(), required=False)

class ActionHistorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(required=False)
    class Meta:
        model = groups_models.ActionHistory
        fields = ('id', 'owner', 'type', 'contents', 'created_at', )
        read_only_fields = ('id', )

class ActionHistoryListSerializer(serializers.Serializer):
    records = serializers.ListField(child=ActionHistorySerializer(), required=True)