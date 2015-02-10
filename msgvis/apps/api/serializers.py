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

class MessageSerializer(serializers.ModelSerializer):
    """
    JSON representation of :class:`.Message`
    objects for the API.

    Messages are provided in a simple format that is useful for displaying
    examples:

    ::

        {
          "id": 52,
          "text": "Some sort of thing or other",
          "sender": "A name",
          "time": "2010-02-25T00:23:53Z"
        }

    Additional fields may be added later.
    """

    model = Message


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
          "dimensions": [
            "time",
            "user"
          ]
        }

    The ``source`` object describes a research article reference where the
    question originated.

    The ``dimensions`` list indicates which dimensions the research question
    is associated with.
    """

    model = Question


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

    model_class = Dimension

class FilterSerializer(serializers.Serializer):
    """
    Filters indicate a subset of the range of a specific dimension. Below is
    an array of three filter objects.

    ::

        [{
          "dimension": 5,
          "min": "2010-02-25T00:23:53Z",
          "max": "2010-02-30T00:23:53Z"
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

    At this time, there are two types of filters:

    -  Quantitative dimensions can be filtered using one or both of the
       ``min`` and ``max`` properties (inclusive).
    -  Categorical dimensions can be filtered by specifying an ``include``
       list. All other items are assumed to be excluded.
    """
