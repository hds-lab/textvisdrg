from django.db import models
from django.db.models import Q

import operator

class Dataset(models.Model):
    """A top-level dataset object containing messages."""

    name = models.CharField(max_length=150)
    """The name of the dataset"""

    description = models.TextField()
    """A description of the dataset."""

    created_at = models.DateTimeField(auto_now_add=True)
    """The :py:class:`datetime.datetime` when the dataset was created."""

    def __unicode__(self):
        return self.name


class MessageType(models.Model):
    """The type of a message, e.g. retweet, reply, original, system..."""

    name = models.CharField(max_length=100, unique=True)
    """The name of the message type"""

    def __unicode__(self):
        return self.name


class Language(models.Model):
    """Represents the language of a message or a user"""

    code = models.SlugField(max_length=10, unique=True)
    """A short language code like 'en'"""

    name = models.CharField(max_length=100)
    """The full name of the language"""

    def __unicode__(self):
        return "%s:%s" % (self.code, self.name)


class Url(models.Model):
    """A url from a message"""

    domain = models.CharField(max_length=100, db_index=True)
    """The root domain of the url"""

    short_url = models.CharField(max_length=250, blank=True)
    """A shortened url"""

    full_url = models.TextField()
    """The full url"""


class Hashtag(models.Model):
    """A hashtag in a message"""

    text = models.CharField(max_length=100)
    """The text of the hashtag, without the hash"""


class Media(models.Model):
    """
    Linked media, e.g. photos or videos.
    """

    type = models.CharField(max_length=50)
    """The kind of media this is."""

    media_url = models.CharField(max_length=250)
    """A url where the media may be accessed"""


class Timezone(models.Model):
    """
    The timezone of a message or user
    """

    olson_code = models.CharField(max_length=40, null=True, blank=True, default=None)
    """The timezone code from pytz."""

    name = models.CharField(max_length=150)
    """Another name for the timezone, perhaps the country where it is located?"""


class Sentiment(models.Model):
    """A sentiment label"""

    value = models.SmallIntegerField(unique=True)
    """A numeric value of the sentiment label"""

    name = models.CharField(max_length=25)
    """The name of the sentiment label"""

    def __unicode__(self):
        return "%d:%s" % (self.value, self.name)


class Topic(models.Model):
    """Topics in messages"""

    name = models.CharField(max_length=100)
    """A short-ish name for the topic"""

    description = models.TextField()
    """A longer description"""


class Person(models.Model):
    """
    A person who sends messages in a dataset.
    """

    dataset = models.ForeignKey(Dataset)
    """Which :class:`Dataset` this person belongs to"""

    original_id = models.BigIntegerField(null=True, blank=True, default=None)
    """An external id for the person, e.g. a user id from Twitter"""

    username = models.CharField(max_length=150, null=True, blank=True, default=None)
    """Username is a short system-y name."""

    full_name = models.CharField(max_length=250, null=True, blank=True, default=None)
    """Full name is a longer user-friendly name"""

    language = models.ForeignKey(Language, null=True, blank=True, default=None)
    """The person's primary :class:`Language`"""

    message_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of messages the person produced"""

    replied_to_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of times the person's messages were replied to"""

    shared_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of times the person's messages were shared or retweeted"""

    mentioned_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of times the person was mentioned in other people's messages"""

    friend_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of people this user has connected to"""

    follower_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of people who have connected to this person"""

    def __unicode__(self):
        return self.username


class Message(models.Model):
    """
    The Message is the central data entity for the dataset.
    """

    dataset = models.ForeignKey(Dataset)
    """Which :class:`Dataset` the message belongs to"""

    original_id = models.BigIntegerField(null=True, blank=True, default=None)
    """An external id for the message, e.g. a tweet id from Twitter"""

    type = models.ForeignKey(MessageType, null=True, blank=True, default=None)
    """The :class:`MessageType` Message type: retweet, reply, origin..."""

    sender = models.ForeignKey(Person, null=True, blank=True, default=None)
    """The :class:`Person` who sent the message"""

    time = models.DateTimeField(null=True, blank=True, default=None)
    """The :py:class:`datetime.datetime` (in UTC) when the message was sent"""

    language = models.ForeignKey(Language, null=True, blank=True, default=None)
    """The :class:`Language` of the message."""

    sentiment = models.ForeignKey(Sentiment, null=True, blank=True, default=None)
    """The :class:`Sentiment` label for message."""

    timezone = models.ForeignKey(Timezone, null=True, blank=True, default=None)
    """The :class:`Timezone` of the message."""

    topics = models.ManyToManyField(Topic, null=True, blank=True, default=None)
    """The set of :class:`Topic` associated with the message."""

    replied_to_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of replies this message received."""

    shared_count = models.PositiveIntegerField(blank=True, default=0)
    """The number of times this message was shared or retweeted."""

    contains_hashtag = models.BooleanField(blank=True, default=False)
    """True if the message has a :class:`Hashtag`."""

    contains_url = models.BooleanField(blank=True, default=False)
    """True if the message has a :class:`Url`."""

    contains_media = models.BooleanField(blank=True, default=False)
    """True if the message has any :class:`Media`."""

    contains_mention = models.BooleanField(blank=True, default=False)
    """True if the message mentions any :class:`Person`."""

    urls = models.ManyToManyField(Url, null=True, blank=True, default=None)
    """The set of :class:`Url` in the message."""

    hashtags = models.ManyToManyField(Hashtag, null=True, blank=True, default=None)
    """The set of :class:`Hashtag` in the message."""

    media = models.ManyToManyField(Media, null=True, blank=True, default=None)
    """The set of :class:`Media` in the message."""

    mentions = models.ManyToManyField(Person, related_name="mentioned_in", null=True, blank=True, default=None)
    """The set of :class:`Person` mentioned in the message."""

    text = models.TextField()
    """The actual text of the message."""

def get_dimension_key(dimension):
    if dimension == "hashtag":
        dimension += "__text"
    elif dimension == "language":
        dimension += "__code"
    elif dimension == "url":
        dimension += "__domain"
    elif dimension == "topic":
        dimension += "__name"
    elif dimension == "sentiment":
        dimension += "__name"
    elif dimension == "timezone":
        dimension += "__name"
    return dimension

def get_example_messages(settings):
    filter_Qs = [Q()]
    filter_predicates = []
    if settings.get("filters"):
        for filter in settings["filters"]:
            if filter.get('min'):
                filter_predicates.append((filter["dimension"] + '__gte', filter.get('min')))
            if filter.get('max'):
                filter_predicates.append((filter["dimension"] + '__lte', filter.get('max')))
            if filter.get('levels'):
                filter_ors = []
                for level in filter.get('levels'):
                    filter_ors.append((get_dimension_key(filter["dimension"]), level))
                filter_Qs.append(reduce(operator.or_, [Q(x) for x in filter_ors]))

    if settings.get("focus"):
        for key in settings["focus"]:
            filter_predicates.append((get_dimension_key(key), settings["focus"][key]))

    filter_Qs.extend([Q(x) for x in filter_predicates])
    final_filters = reduce(operator.and_, filter_Qs)
    return Message.objects.filter(final_filters)[:10]
