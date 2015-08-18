"""
Import this module to get access to dimension instances.

.. code-block:: python

    from msgvis.apps.dimensions import registry
    time = registry.get_dimension('time') # returns a TimeDimension
    time.get_distribution(a_dataset)

"""
from msgvis.apps.dimensions import models

_dimension_registry = {}
_create_params = {}

def register(dimensionClass, kwargs):
    """Register a dimension"""
    key = kwargs['key']
    if key in _create_params:
        raise KeyError("The dimension %s is already registered." % key)

    _create_params[key] = (dimensionClass, kwargs)

def get_dimension(dimension_key):
    """Get a specific dimension by key"""

    if dimension_key not in _dimension_registry:
        # Create if it hasn't been instantiated
        dimensionClass, kwargs = _create_params.pop(dimension_key)
        _dimension_registry[kwargs['key']] = dimensionClass(**kwargs)

    return _dimension_registry[dimension_key]


def get_dimensions():
    """Get a list of all the registered dimensions."""

    # First create all the uninstantiated dimensions
    if len(_create_params) > 0:
        for key in _create_params.keys():
            get_dimension(key)

    return _dimension_registry.values()


def get_dimension_ids():
    """Get a list of all the dimension keys."""

    # First create all the uninstantiated dimensions
    if len(_create_params) > 0:
        for key in _create_params.keys():
            get_dimension(key)

    return _dimension_registry.keys()




# BEGIN TIME DIMENSIONS
register(models.TimeDimension, dict(
    key='time',
    name='Time',
    description='The time the message was sent',
    field_name='time',
))

register(models.RelatedCategoricalDimension, dict(
    key='timezone',
    name='Timezone',
    description="The message sender's local timezone",
    field_name='timezone__name',
))
# END TIME DIMENSIONS

# BEGIN CONTENT DIMENSIONS
register(models.RelatedCategoricalDimension, dict(
    key='topics',
    name='Topic',
    description='Topics found in the message.',
    field_name='topics__name',
))

register(models.TextDimension, dict(
    key='words',
    name='Keywords',
    description='The words found in the message',
    field_name='words__text',
))

register(models.RelatedCategoricalDimension, dict(
    key='hashtags',
    name='Hashtags',
    description='Hashtags in the message',
    field_name='hashtags__text',
))

register(models.CategoricalDimension, dict(
    key='contains_hashtag',
    name='Contains a Hashtag',
    description='Contains any hashtag',
    field_name='contains_hashtag',
    domain=[False, True],
))

register(models.RelatedCategoricalDimension, dict(
    key='urls',
    name='Urls',
    description='Urls in the message',
    field_name='urls__domain',
))

register(models.CategoricalDimension, dict(
    key='contains_url',
    name='Contains a Url',
    description='Contains a url',
    field_name='contains_url',
    domain=[False, True],
))

register(models.RelatedCategoricalDimension, dict(
    key='media',
    name='Media',
    description='Photos in the message',
    field_name='media__type',
))

register(models.CategoricalDimension, dict(
    key='contains_media',
    name='Contains Media',
    description='Contains a photo',
    field_name='contains_media',
    domain=[False, True],
))

# END CONTENT DIMENSIONS

# BEGIN META DIMENSIONS
register(models.RelatedCategoricalDimension, dict(
    key='language',
    name='Language',
    description='The language of the message',
    field_name='language__name',
))

register(models.ChoicesCategoricalDimension, dict(
    key='sentiment',
    name='Sentiment',
    description='The sentiment of the message',
    field_name='sentiment',
))
# END META DIMENSIONS

# BEGIN INTERACTIONS DIMENSIONS
register(models.RelatedCategoricalDimension, dict(
    key='type',
    name='Message type',
    description='The type of message',
    field_name='type__name',
))

register(models.QuantitativeDimension, dict(
    key='replies',
    name='Num. Replies',
    description='How many replies the message received',
    field_name='replied_to_count',
))

register(models.QuantitativeDimension, dict(
    key='shares',
    name='Num. Shares',
    description='How many times the message was shared or retweeted',
    field_name='shared_count',
))

register(models.RelatedCategoricalDimension, dict(
    key='mentions',
    name='Mentions',
    description='Usernames mentioned in the message',
    field_name='mentions__username',
))

register(models.CategoricalDimension, dict(
    key='contains_mention',
    name='Contains a mention',
    description='Mentions any username',
    field_name='contains_mention',
    domain=[False, True],
))

# END INTERACTIONS DIMENSIONS

# BEGIN SENDER DIMENSIONS
register(models.RelatedCategoricalDimension, dict(
    key='sender_name',
    name='Author Name',
    description='The name of the message author',
    field_name='sender__username',
))

register(models.RelatedQuantitativeDimension, dict(
    key='sender_message_count',
    name='Num. Messages',
    description="The author's total number of messages",
    field_name='sender__message_count',
))

register(models.RelatedQuantitativeDimension, dict(
    key='sender_reply_count',
    name='Num. Replies',
    description="The total replies the author has received",
    field_name='sender__replied_to_count',
))

register(models.RelatedQuantitativeDimension, dict(
    key='sender_mention_count',
    name='Num. Mentions',
    description="The total times the author has been mentioned",
    field_name='sender__mentioned_count',
))

register(models.RelatedQuantitativeDimension, dict(
    key='sender_share_count',
    name='Num. Shares',
    description="The total shares or retweets the author has received",
    field_name='sender__shared_count',
))

register(models.RelatedQuantitativeDimension, dict(
    key='sender_friend_count',
    name='Num. Friends',
    description="The number of people the author has connected to",
    field_name='sender__friend_count',
))

register(models.RelatedQuantitativeDimension, dict(
    key='sender_follower_count',
    name='Num. Followers',
    description="The number of people who have connected to the author",
    field_name='sender__follower_count',
))
# END SENDER DIMENSIONS

register(models.RelatedCategoricalDimension, dict(
    key='groups',
    name='Groups',
    description='Groups of message',
    field_name='groups__id',
))
