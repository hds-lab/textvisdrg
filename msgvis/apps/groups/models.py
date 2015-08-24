from django.db import models
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.enhance import models as enhance_models

class Group(models.Model):
    """
    A group of messages, created by inclusive and exclusive keywords.
    """

    name = models.CharField(max_length=250, default=None, blank=True)
    """The group name."""

    dataset = models.ForeignKey(corpus_models.Dataset)
    """Which :class:`corpus_models.Dataset` this group belongs to"""

    created_at = models.DateTimeField(auto_now_add=True)
    """Creation time"""

    inclusive_keywords = models.ManyToManyField(enhance_models.Word, null=True, blank=True, default=None, related_name='inclusive_keywords')
    """The set of :class:`enhance_models.Word` as inclusive keywords."""

    exclusive_keywords = models.ManyToManyField(enhance_models.Word, null=True, blank=True, default=None, related_name='exclusive_keywords')
    """The set of :class:`enhance_models.Word` as exclusive keywords."""

    messages = models.ManyToManyField(corpus_models.Message, null=True, blank=True, default=None, related_name='groups')
    """The set of :class:`corpus_models.Message` that belong to this group."""


    def message_list(self):
        results = set()

        dictionary = self.dataset.dictionary.all()
        if len(dictionary) > 0:
            dictionary = dictionary[0]
            inclusive_keywords = self.inclusive_keywords.all()
            exclusive_keywords = self.exclusive_keywords.all()
            if len(inclusive_keywords) > 0:
                for keyword in inclusive_keywords:
                    word = dictionary.words.get(text=keyword)
                    if word is not None:
                        for msg in word.messages.all():
                            flag = True
                            for exclusive_keyword in exclusive_keywords:
                                exclusive_word = dictionary.words.get(text=exclusive_keyword)
                                if exclusive_word in msg.words.all():
                                    flag = False
                                    break
                            if flag is True:
                                results.add(msg)
            elif len(exclusive_keywords) > 0:
                for msg in corpus_models.Message.objects.filter(dataset=self.dataset):
                    flag = True
                    for exclusive_keyword in exclusive_keywords:
                        exclusive_word = dictionary.words.get(text=exclusive_keyword)
                        if exclusive_word in msg.words.all():
                            flag = False
                            break
                    if flag is True:
                        results.add(msg)
        #return len(list(results))
        return list(results)

    def update_messages_in_group(self):
        self.messages.clear()
        inclusive_keywords = map(lambda x: x.text, self.inclusive_keywords.all())
        exclusive_keywords = map(lambda x: x.text, self.exclusive_keywords.all())
        self.messages = self.dataset.get_advanced_search_results(inclusive_keywords, exclusive_keywords)
        #print "message count:" + str(self.messages.count())



    @property
    def messages_online(self):
        inclusive_keywords = map(lambda x: x.text, self.inclusive_keywords.all())
        exclusive_keywords = map(lambda x: x.text, self.exclusive_keywords.all())
        return self.dataset.get_advanced_search_results(inclusive_keywords, exclusive_keywords)

    @property
    def message_count(self):
        return self.messages.count()


    def add_inclusive_keywords(self, keywords):
        self.inclusive_keywords.clear()
        dictionary = self.dataset.get_dictionary()
        if dictionary is not None:
            if keywords:
                for in_keyword in keywords:
                    word = dictionary.words.filter(text=in_keyword)
                    if word.count() > 0:
                        self.inclusive_keywords.add(word[0])

    def add_exclusive_keywords(self, keywords):
        self.exclusive_keywords.clear()
        dictionary = self.dataset.get_dictionary()
        if dictionary is not None:
            if keywords:
                for ex_keyword in keywords:
                    word = dictionary.words.filter(text=ex_keyword)
                    if word.count() > 0:
                        self.exclusive_keywords.add(word[0])


    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.__repr__()

