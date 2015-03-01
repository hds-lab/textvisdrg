from django.test import TestCase

import mock
from templatetags import active

from msgvis.apps.corpus import models as corpus_models


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

    def create_empty_dataset(self):
        return corpus_models.Dataset.objects.create(
            name="Test empty dataset",
            description="Created by create_empty_dataset",
        )

    def generate_messages_for_distribution(self, field_name, distribution, many=False, dataset=None):
        """
        Generates a bunch of messages for testing.
        On each message, the given field will be set to some value,
        according to the distribution indicating how often
        each value should occur. Returns a dataset
        containing the messages.
        """

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

    def convert_id_distribution_to_related(self, id_distribution, model_classes, field_names):
        """
        Provide a distribution with keys that are tuples of ids or single ids.
        Provide a model class or a tuple of model classes that the ids belong to.
        Provide a field name on the model, or field names on the corresponding model.

        Produces a new distribution with the ids replaced by the values of
        the field on the corresponding model.
        """
        is_multi = isinstance(model_classes, (tuple, list))

        # convert to tuples to simplify the code below
        model_tuple = model_classes if is_multi else (model_classes, )
        field_tuple = field_names if is_multi else (field_names, )

        result = {}
        for idkey, value in id_distribution.iteritems():
            # convert to tuple
            idtuple = idkey if is_multi else (idkey,)

            # Find the model for each id
            field_values = []
            for id, model, field in zip(idtuple, model_tuple, field_tuple):
                obj = model.objects.get(id=id)
                field_values.append(getattr(obj, field))

            # Convert back to single if needed
            if not is_multi:
                field_values = field_values[0]
            else:
                field_values = tuple(field_values)  # tuples are hashable

            # Store the result in the new distribution
            if field_values not in result:
                result[field_values] = 0  # start a count at 0

            # Add the value
            result[field_values] += value

        return result

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

    def generate_messages_for_multi_distribution(self, field_names, distribution, dataset=None):
        """
        Generate a messages for a multi-valued distribution.

        Field names should be an ordered list of which fields are being set.
        The distribution should be a dictionary with keys as tuples
        containing the values of the fields, in the same order.
        The values in the distribution dictionary indicate how many messages to create.
        """

        if dataset is None:
            dataset = corpus_models.Dataset.objects.create(
                name="Test %s distribution" % ':'.join(field_names),
                description="Created by create_multi_distribution",
            )

        num = 0
        for value_tuple, count in distribution.iteritems():
            for i in range(count):
                field_values = dict(zip(field_names, value_tuple))

                field_values['text'] = "Message %d: '%s'" % (num, str(field_values))
                msg = dataset.message_set.create(**field_values)

                num += 1

        return dataset

    def convert_dictresults_to_distribution(self, dict_results, field_names, measure_key='count'):
        """
        Input is a list of dictionaries with keys from field_names and measure_key.

        Each input dictionary is converted to a tuple (or single) for its field name values, and the measure.
        This is entered into a distribution dictionary that maps field values to measure values.
        """
        is_multi = isinstance(field_names, (tuple, list))

        # Convert to tuples for processing
        field_names_tuple = field_names if is_multi else tuple(field_names)

        distribution = {}
        for row in dict_results:

            # Get the field values in order
            field_values_tuple = tuple(row[fname] for fname in field_names_tuple)
            # Get the measure value
            measure = row[measure_key]

            if not is_multi:
                # Unconvert to tuples if necessary
                field_values_tuple = field_values_tuple[0]

            distribution[field_values_tuple] = measure

        return distribution

    def assertMultiDistributionsEqual(self, result, desired_distribution, field_names, measure_key='count'):
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
            # Each row should have the measure and levels for each field
            self.assertIn(measure_key, row)
            for fname in field_names:
                self.assertIn(fname, row)

            values = row.copy()
            values.pop(measure_key)
            # A list of the field values in order
            unzipped_values = tuple(values[fname] for fname in field_names)
            count = row[measure_key]

            # Check that this combo of levels was expected
            self.assertIn(unzipped_values, desired_distribution)
            # check the count is actually correct
            self.assertEquals(count, desired_distribution[unzipped_values])

            if count == 0:
                # It was zero but was included anyway
                del zeros[unzipped_values]

        # Should match the length of the distribution
        self.assertEquals(len(result), len(desired_distribution) - len(zeros))

    def create_test_languages(self):
        """Create a bunch of languages and get a list of ids."""

        for val in [("en", "English"), ("jp", "Japanese"), ("fr", "French")]:
            corpus_models.Language.objects.create(
                code=val[0],
                name=val[1]
            )

        return corpus_models.Language.objects.values_list('id', flat=True).distinct()

    def create_test_hashtags(self, num_hashtags=5):
        """Create a bunch of hashtags and get a list of ids."""

        # Create some hashtags
        for ht in range(num_hashtags):
            corpus_models.Hashtag.objects.create(
                text="#ht%d" % ht
            )

        return corpus_models.Hashtag.objects.values_list('id', flat=True).distinct()

    def create_authors_with_values(self, field_name, values, dataset=None):
        """Generate a dataset and a set of authors with fields set to the given values."""

        if dataset is None:
            dataset = corpus_models.Dataset.objects.create(
                name="Test author name distribution",
                description="Created by test_author_name_distribution",
            )

        # Create some authors
        for value in values:
            corpus_models.Person.objects.create(**{'dataset': dataset, field_name: value})

        return dataset

    def distibute_messages_to_authors(self, dataset):
        """Create messages for each author, and return a dict of author id to message count."""
        author_ids = dataset.person_set.values_list('id', flat=True).distinct()
        author_distribution = self.get_distribution(author_ids)

        self.generate_messages_for_distribution(
            field_name='sender_id',
            distribution=author_distribution,
            dataset=dataset,
        )
        return author_distribution
