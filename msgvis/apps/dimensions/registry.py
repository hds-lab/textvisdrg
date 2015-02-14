from msgvis.apps.dimensions import models

_dimension_registry = {}


def register(dimension):
    key = dimension.key
    if key in _dimension_registry:
        raise KeyError("The dimension %s is already registered." % key)

    _dimension_registry[key] = dimension


def get_dimension(dimension_key):
    return _dimension_registry.get(dimension_key)

def get_dimensions():
    return _dimension_registry.values()

def get_dimension_ids():
    return _dimension_registry.keys()

# BEGIN TIME DIMENSIONS
register(models.TimeDimension(
    key='time',
    name='Time',
    description='The time the message was sent',
    field_name='time',
))

register(models.ForeignKeyDimension(
    key='timezone',
    name='Timezone',
    description="The message sender's local timezone",
    field_name='timezone',
))
# END TIME DIMENSIONS

# BEGIN CONTENT DIMENSIONS
register(models.ForeignKeyDimension(
    key='topics',
    name='Topic',
    description='Topics found in the message.',
    field_name='topics',
))

register(models.TextDimension(
    key='words',
    name='Keywords',
    description='The words found in the message',
    field_name='text',
))

register(models.ForeignKeyDimension(
    key='hashtags',
    name='Hashtags',
    description='Hashtags in the message',
    field_name='hashtags',
))

register(models.ForeignKeyDimension(
    key='urls',
    name='Urls',
    description='Urls in the message',
    field_name='urls',
))

register(models.ForeignKeyDimension(
    key='media',
    name='Media',
    description='Photos in the message',
    field_name='media',
))
# END CONTENT DIMENSIONS

# BEGIN META DIMENSIONS
register(models.ForeignKeyDimension(
    key='language',
    name='Language',
    description='The language of the message',
    field_name='language',
))

register(models.ForeignKeyDimension(
    key='sentiment',
    name='Sentiment',
    description='The sentiment of the message',
    field_name='sentiment',
))
# END META DIMENSIONS

# BEGIN INTERACTIONS DIMENSIONS
register(models.ForeignKeyDimension(
    key='type',
    name='Message type',
    description='The type of message',
    field_name='type',
))

register(models.QuantitativeDimension(
    key='replies',
    name='Num. Replies',
    description='How many replies the message received',
    field_name='replied_to_count',
))

register(models.QuantitativeDimension(
    key='shares',
    name='Num. Shares',
    description='How many times the message was shared or retweeted',
    field_name='shared_count',
))

register(models.ForeignKeyDimension(
    key='mentions',
    name='Mentions',
    description='Usernames mentioned in the message',
    field_name='mentions',
))
# END INTERACTIONS DIMENSIONS

# BEGIN AUTHOR DIMENSIONS
register(models.CategoricalDimension(
    key='author_name',
    name='Author name',
    description='The name of the message author',
    field_name='sender__name',
))

register(models.QuantitativeDimension(
    key='author_message_count',
    name='Num. Messages',
    description="The author's total number of messages",
    field_name='sender__message_count',
))

register(models.QuantitativeDimension(
    key='author_reply_count',
    name='Num. Replies',
    description="The total replies the author has received",
    field_name='sender__replied_to_count',
))

register(models.QuantitativeDimension(
    key='author_mention_count',
    name='Num. Mentions',
    description="The total times the author has been mentioned",
    field_name='sender__mentioned_count',
))

register(models.QuantitativeDimension(
    key='author_share_count',
    name='Num. Shares',
    description="The total shares or retweets the author has received",
    field_name='sender__shared_count',
))

register(models.QuantitativeDimension(
    key='author_friend_count',
    name='Num. Friends',
    description="The number of people the author has connected to",
    field_name='sender__friend_count',
))

register(models.QuantitativeDimension(
    key='author_follower_count',
    name='Num. Followers',
    description="The number of people who have ocnnected to the author",
    field_name='sender__follower_count',
))
# END AUTHOR DIMENSIONS
