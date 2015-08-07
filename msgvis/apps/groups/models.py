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

    @property
    def messages(self):
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
        return list(results)

    def __repr__(self):
        return self.title

    def __unicode__(self):
        return self.__repr__()

