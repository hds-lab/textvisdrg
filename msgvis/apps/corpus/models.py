import operator
from django.db import models
from django.db.models import Q
from caching.base import CachingManager, CachingMixin

from msgvis.apps.base import models as base_models
from msgvis.apps.corpus import utils

import re

import os
from msgvis.settings.common import DEBUG


class Dataset(models.Model):
    """A top-level dataset object containing messages."""

    name = models.CharField(max_length=150)
    """The name of the dataset"""

    description = models.TextField()
    """A description of the dataset."""

    created_at = models.DateTimeField(auto_now_add=True)
    """The :py:class:`datetime.datetime` when the dataset was created."""

    start_time = models.DateTimeField(null=True, default=None, blank=True)
    """The time of the first real message in the dataset"""

    end_time = models.DateTimeField(null=True, default=None, blank=True)
    """The time of the last real message in the dataset"""

    def __unicode__(self):
        return self.name

    def get_example_messages(self, filters=[], excludes=[]):
        """Get example messages given some filters (dictionaries containing dimensions and filter params)"""

        messages = self.message_set.all()

        for filter in filters:
            dimension = filter["dimension"]

            # Remove the dimension key
            params = {key: value for key, value in filter.iteritems() if key != "dimension"}

            messages = dimension.filter(messages, **params)

        for exclude in excludes:
            dimension = exclude["dimension"]

            # Remove the dimension key
            params = {key: value for key, value in excludes.iteritems() if key != "dimension"}

            messages = dimension.exclude(messages, **params)

        return messages

    def get_example_messages_by_groups(self, groups, filters=[], excludes=[]):
        include_groups = map(lambda x: int(x['value']), filter(lambda x: x['dimension'].key=='groups', filters))
        if len(include_groups)> 0:
            groups = include_groups
        exclude_groups = map(lambda x: int(x['value']), filter(lambda x: x['dimension'].key=='groups', excludes))
        groups = filter(lambda x: x not in exclude_groups, groups)

        per_group = int(10 / len(groups))
        combined_messages = []
        group_querysets = []
        for group in groups:
            group_obj = self.groups.get(id=group)
            messages = group_obj.messages
            for filterA in filters:
                dimension = filterA["dimension"]

                # Remove the dimension key
                params = {key: value for key, value in filterA.iteritems() if key != "dimension"}
                messages = dimension.filter(messages, **params)

            for exclude in excludes:
                dimension = exclude["dimension"]

                # Remove the dimension key
                params = {key: value for key, value in excludes.iteritems() if key != "dimension"}

                messages = dimension.exclude(messages, **params)

            group_querysets.append(messages)
            #combined_messages.extend(messages[:per_group])
        query = ""
        for idx, queryset in enumerate(group_querysets):
            if idx > 0:
                query += " UNION "
            query += "(%s)" %(utils.quote(str(queryset.query)))
        query = utils.convert_boolean(query)
        queryset = Message.objects.raw(query)
        return queryset

    def get_dictionary(self):
        dictionary = self.dictionary.all()
        if len(dictionary) > 0:
            dictionary = dictionary[0]
            return dictionary
        return None

    def get_advanced_search_results(self, inclusive_keywords, exclusive_keywords):

        queryset = self.message_set.all()
        if len(inclusive_keywords) > 0:
            #inclusive_keywords = map(lambda x: ("words__text__icontains", x), inclusive_keywords)
            #inclusive_keywords = map(lambda x: ("words__text", x), inclusive_keywords)
            #queryset = queryset.filter(reduce(operator.and_, [Q(x) for x in inclusive_keywords]))
            queryset = Message.objects.all()
            for inclusive_keyword in inclusive_keywords:
                queryset &= inclusive_keyword.messages.all()
            #print queryset.count()

        if len(exclusive_keywords) > 0:
            #exclusive_keywords = map(lambda x: ("words__text__icontains", x), exclusive_keywords)
            #for word in exclusive_keywords:
            #    queryset = queryset.exclude(words__text=word.text)
            exclusive_keywords = map(lambda x: x.text, exclusive_keywords)
            queryset = queryset.exclude(utils.levels_or("words__text", exclusive_keywords))
            #print queryset.count()
        return queryset

    def get_precalc_distribution(self, dimension, search_key=None, page=None, page_size=100, mode=None):
        dimension_key = dimension.key
        distribution = self.distributions.filter(dimension_key=dimension_key)
        if search_key is not None:
            distribution = distribution.filter(level__icontains=search_key)
        distribution = distribution.order_by('-count')
        total_num_levels = distribution.count()
        if page is not None:
            start = (page - 1) * page_size
            end = min(start + page_size, total_num_levels)
            max_page = (total_num_levels / page_size) + 1

            # no level left
            if total_num_levels == 0 or start > total_num_levels:
                return None

            distribution = distribution[start:end]

        else:
            if mode == "omit_others" or mode == "enable_others":
                MAX_CATEGORICAL_LEVELS = 10
                distribution = distribution[:MAX_CATEGORICAL_LEVELS]
            else:
                distribution = distribution.all()

        domains = {}
        domain_labels = {}

        domain = map(lambda x: x.level, distribution)
        labels = dimension.get_domain_labels(domain)

        domains[dimension_key] = domain
        domain_labels[dimension_key] = labels

        table = map(lambda x: {dimension_key: x.level, "value": x.count}, distribution)

        results = {
            "table": table,
            "domains": domains,
            "domain_labels": domain_labels
        }

        return results




class MessageType(CachingMixin, models.Model):
    """The type of a message, e.g. retweet, reply, original, system..."""

    name = models.CharField(max_length=100, unique=True)
    """The name of the message type"""

    objects = CachingManager()

    def __unicode__(self):
        return self.name


class Language(CachingMixin, models.Model):
    """Represents the language of a message or a user"""

    code = models.SlugField(max_length=10, unique=True)
    """A short language code like 'en'"""

    name = models.CharField(max_length=100)
    """The full name of the language"""

    objects = CachingManager()

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

    text = base_models.Utf8CharField(max_length=100, db_index=True)
    """The text of the hashtag, without the hash"""


class Media(models.Model):
    """
    Linked media, e.g. photos or videos.
    """

    type = models.CharField(max_length=50)
    """The kind of media this is."""

    media_url = models.CharField(max_length=250)
    """A url where the media may be accessed"""


class Timezone(CachingMixin, models.Model):
    """
    The timezone of a message or user
    """

    olson_code = models.CharField(max_length=40, null=True, blank=True, default=None)
    """The timezone code from pytz."""

    name = models.CharField(max_length=150, db_index=True)
    """Another name for the timezone, perhaps the country where it is located?"""

    objects = CachingManager()


class Person(models.Model):
    """
    A person who sends messages in a dataset.
    """

    class Meta:
        index_together = (
            ('dataset', 'original_id')  # used by the importer
        )

    dataset = models.ForeignKey(Dataset)
    """Which :class:`Dataset` this person belongs to"""

    original_id = models.BigIntegerField(null=True, blank=True, default=None)
    """An external id for the person, e.g. a user id from Twitter"""

    username = base_models.Utf8CharField(max_length=150, null=True, blank=True, default=None)
    """Username is a short system-y name."""

    full_name = base_models.Utf8CharField(max_length=250, null=True, blank=True, default=None)
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

    profile_image_url = models.TextField(null=True, blank=True, default="")
    """The person's profile image url"""

    def __unicode__(self):
        return self.username

    @property
    def profile_image_local_name(self):
        if DEBUG or os.environ["DJANGO_SETTINGS_MODULE"] == "msgvis.settings.test":
            return "profile_1000204970.jpeg"

        url = self.profile_image_url
        if url != "":
            pattern = re.compile('/\w+\.([_\w]+)$')
            results = pattern.search(url)
            if results:
                suffix = results.groups()[0]
                url = "profile_" + str(self.original_id) + "." + suffix

        return url
        


class Message(models.Model):
    """
    The Message is the central data entity for the dataset.
    """
    class Meta:
        index_together = (
            ('dataset', 'original_id'),  # used by importer
            ('dataset', 'time'),
        )
            
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

    SENTIMENT_POSITIVE = 1
    SENTIMENT_NEUTRAL  = 0
    SENTIMENT_NEGATIVE = -1
    SENTIMENT_CHOICES = (
        (SENTIMENT_POSITIVE, "positive"),
        (SENTIMENT_NEUTRAL,  "neutral"),
        (SENTIMENT_NEGATIVE, "negative")
    )

    sentiment = models.SmallIntegerField(choices=SENTIMENT_CHOICES, null=True, blank=True, default=None)
    """The sentiment label for message."""

    timezone = models.ForeignKey(Timezone, null=True, blank=True, default=None)
    """The :class:`Timezone` of the message."""

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

    text = base_models.Utf8TextField(null=True, blank=True, default="")
    """The actual text of the message."""

    @property
    def embedded_html(self):
        #return utils.get_embedded_html(self.original_id)
        return utils.render_html_tag(self.text)

    @property
    def media_url(self):
        url = ""
        if self.contains_media:
            url = self.media.all()[0].media_url
            pattern = re.compile('/(\w+\.[_\-\w]+)$')
            results = pattern.search(url)
            if results:
                url = results.groups()[0]
        return url


    def __repr__(self):
        return str(self.time) + " || " + self.text

    def __unicode__(self):
        return self.__repr__()




