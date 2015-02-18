from django.test import TestCase

import mock
from templatetags import active


class TemplateTagActiveTest(TestCase):
    def test_matches_request_path(self):
        request = mock.Mock()
        request.path = "/foo/bar"

        result = active.active(request, r'^/foo/')
        self.assertEquals(result, 'active')

        result = active.active(request, r'^/abcd/')
        self.assertEquals(result, '')

        result = active.active(request, r'^/')
        self.assertEquals(result, 'active')

        result = active.active(request, r'^/foo/$')
        self.assertEquals(result, '')


class DistributionTestCaseMixins(object):
    """Some utilities for working with distributions"""

    def get_distribution(self, values, min_count=5):
        """Get a dictionary containing a (deterministic) distribution over the values"""
        distrib = {}
        for idx, value in enumerate(values):
            distrib[value] = min_count + idx
        return distrib

    def generate_messages_for_distribution(self, field_name, distribution, many=False, dataset=None):
        """
        Generates a bunch of messages for testing.
        On each message, the given field will be set to some value,
        according to the distribution indicating how often
        each value should occur. Returns a dataset
        containing the messages.
        """
        from msgvis.apps.corpus import models as corpus_models

        if dataset is None:
            dataset = corpus_models.Dataset.objects.create(
                name="Test %s distribution" % field_name,
                description="Created by generate_message_distribution",
                )

        num = 0
        for value, count in distribution.iteritems():
            for i in range(count):
                create_params = {
                    'text': "Message %d: %s = '%s'" % (num, field_name, value),
                    }

                if not many:
                    # If it's a flat field, we just send the value at this point
                    create_params[field_name] = value

                msg = dataset.message_set.create(**create_params)

                if many:
                    # Otherwise we need to add it after the fact
                    getattr(msg, field_name).add(value)

                num += 1

        return dataset

    def recover_related_field_distribution(self, id_distribution, model_class, field_name):
        """
        Given a dict of author id to message count,
        produces a dict of author field values to message counts.

        If there are multiple authors with the same field value,
        their message counts will be added.
        """
        field_distribution = {}
        for pid, pcount in id_distribution.iteritems():
            obj = model_class.objects.get(id=pid)

            field_val = getattr(obj, field_name)
            if field_val not in field_distribution:
                field_distribution[field_val] = 0

            field_distribution[field_val] += pcount

        return field_distribution


    def assertDistributionsEqual(self, result, desired_distribution, level_key='value', measure_key='count'):
        """
        Confirms the messages in the dataset match the distribution for the given field.
        Allows for missing entries in the result due to zeros.
        """

        # It's alright if it is missing zero-count values.
        zeros = {}
        for value, count in desired_distribution.iteritems():
            if count == 0:
                zeros[value] = count

        for row in result:
            # check the result row value is in the distribution
            value = row[level_key]
            count = row[measure_key]

            # check the count is correct
            self.assertIn(value, desired_distribution)
            self.assertEquals(count, desired_distribution[value])

            if count == 0:
                del zeros[value]

        # Should match the length of the distribution
        self.assertEquals(len(result), len(desired_distribution) - len(zeros))
