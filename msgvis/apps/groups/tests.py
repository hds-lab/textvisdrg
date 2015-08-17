from django.test import TestCase
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.groups.models import Group
from msgvis.apps.enhance import models as enhance_models

import json

# Create your tests here.
class GroupTest(TestCase):

    def add_word_msg_connection(self, dictionary, word, msg):
        enhance_models.MessageWord.objects.create(
            dictionary=dictionary,
            word=word,
            message=msg,
            word_index=word.index,
            count = 1,
            tfidf = 0.5
        )

    def generate_some_messages(self, dataset):

        msg1 = corpus_models.Message.objects.create(
            dataset=dataset,
            text="blah blah blah apple pink yellow",
            time="2015-02-02T01:19:02Z",
            shared_count=0,
        )

        msg2 = corpus_models.Message.objects.create(
            dataset=dataset,
            text="blah blah blah apple pink yellow book",
            time="2015-02-02T01:19:02Z",
            shared_count=0,
        )

        msg3 = corpus_models.Message.objects.create(
            dataset=dataset,
            text="QQ OAO book",
            time="2015-02-02T01:19:02Z",
            shared_count=0,
        )

        dictionary = enhance_models.Dictionary.objects.create(
            dataset=dataset,
            name="Test Dictionary",
            settings=""
        )
        word_list = ["yellow", "pink", "blah", "apple", "QQ", "book", "OAO"]
        self.word_obj_dict = {}
        for i, word in enumerate(word_list):
            word_obj = enhance_models.Word.objects.create(
                dictionary=dictionary,
                index=i,
                text=word,
                document_frequency=1
            )
            self.word_obj_dict[word] = word_obj

        self.add_word_msg_connection(dictionary, self.word_obj_dict["blah"], msg1)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["apple"], msg1)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["pink"], msg1)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["yellow"], msg1)

        self.add_word_msg_connection(dictionary, self.word_obj_dict["blah"], msg2)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["apple"], msg2)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["pink"], msg2)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["yellow"], msg2)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["book"], msg2)

        self.add_word_msg_connection(dictionary, self.word_obj_dict["QQ"], msg3)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["OAO"], msg3)
        self.add_word_msg_connection(dictionary, self.word_obj_dict["book"], msg3)

        return [msg1, msg2, msg3]

    def create_some_groups(self):
        groups = []

        group1 = Group.objects.create(
            name="group 1",
            dataset=self.dataset
        )
        group1.inclusive_keywords.add(self.word_obj_dict["blah"])
        group1.save()
        group1.update_messages_in_group()
        groups.append(group1)

        group2 = Group.objects.create(
            name="group 2",
            dataset=self.dataset
        )
        group2.exclusive_keywords.add(self.word_obj_dict["QQ"])
        group2.save()
        group2.update_messages_in_group()
        groups.append(group2)

        group3 = Group.objects.create(
            name="group 3",
            dataset=self.dataset
        )
        group3.inclusive_keywords.add(self.word_obj_dict["book"])
        group3.exclusive_keywords.add(self.word_obj_dict["QQ"])
        group3.save()
        group3.update_messages_in_group()
        groups.append(group3)

        group4 = Group.objects.create(
            name="group 4",
            dataset=self.dataset
        )
        group4.inclusive_keywords.add(self.word_obj_dict["blah"])
        group4.inclusive_keywords.add(self.word_obj_dict["book"])
        group4.exclusive_keywords.add(self.word_obj_dict["QQ"])
        group4.save()
        group4.update_messages_in_group()
        groups.append(group4)

        return groups

    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")
        self.messages = self.generate_some_messages(self.dataset)
        self.groups = self.create_some_groups()


    def test_basic_connections(self):
        self.assertEquals(len(self.word_obj_dict["blah"].messages.all()), 2)
        self.assertEquals(len(self.word_obj_dict["QQ"].messages.all()), 1)

        self.assertEquals(len(self.messages[0].words.all()), 4)
        self.assertEquals(len(self.messages[1].words.all()), 5)
        self.assertEquals(len(self.messages[2].words.all()), 3)



    def test_get_messages(self):
        self.assertEquals(self.groups[0].message_count, 2)
        self.assertEquals(self.groups[1].message_count, 2)
        self.assertEquals(self.groups[2].message_count, 1)
        self.assertEquals(self.groups[3].message_count, 2)

    
