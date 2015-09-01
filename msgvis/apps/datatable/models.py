from django.db import models
from django.db.models import Q
from datetime import timedelta
import operator

from msgvis.apps.base.models import MappedValuesQuerySet
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.groups import models as groups_models
from msgvis.apps.dimensions import registry

import re
from django.db import connection

MAX_CATEGORICAL_LEVELS = 10

def find_messages(queryset):
    """If the given queryset is actually a :class:`.Dataset` model, get its messages queryset."""
    if isinstance(queryset, corpus_models.Dataset):
        queryset = queryset.message_set.all()
    return queryset

def levels_or(field_name, domain):
    filter_ors = []
    for level in domain:
        if level is None or level == "":
            filter_ors.append((field_name + "__isnull", True))
        else:
            filter_ors.append((field_name, level))

    return reduce(operator.or_, [Q(x) for x in filter_ors])

def quote_query(matchobj):
    return "'" + matchobj.group(0) + "'"

def quote(text):
    pattern = r'(?<== )\d+\-\d+\-\d+ \d+:\d+:\d+|(?<== )[\da-zA-Z_#\-.]+(?=[ )])'
    text = re.sub(pattern, quote_query, text)
    return text

def get_field_name(text):
    pattern = re.compile('(?<=__)\w+')
    results = pattern.search(text)
    if results:
        return results.group()
    return None

def fetchall(sql):
    "Returns all rows from a cursor as a dict"
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    return [
        row[0]
        for row in cursor.fetchall()
    ]

def fetchall_table(sql):
    "Returns all rows from a cursor as a dict"
    cursor = connection.cursor()
    cursor.execute(sql)
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def group_messages_by_dimension_with_raw_query(query, dimension, callback):
    queryset = corpus_models.Message.objects.raw(query)
    message_id = corpus_models.Message._meta.model_name + "_id" #message_id
    fieldname = get_field_name(dimension.field_name)
    key = dimension.key
    related_mgr = getattr(corpus_models.Message, dimension.key)
    if hasattr(related_mgr, "RelatedObjectDoesNotExist"):
        related_table = related_mgr.field.rel.to._meta.db_table
        related_id = related_mgr.field.rel.to._meta.model._meta.model_name + "_id"
        if related_id == "person_id":
            related_id = "sender_id"
        elif related_id == "messagetype_id":
            related_id = "type_id"
        final_query = "SELECT B.%s AS `%s`, count(*) AS `value` FROM (%s) AS A, `%s` AS B WHERE A.%s=B.id GROUP BY B.%s ORDER BY `value` DESC" %(fieldname, key, query, related_table, related_id, fieldname)

    else:
        if hasattr(related_mgr, "field"):
            through_table = related_mgr.through._meta.db_table  # e.g., corpus_message_hashtags
            related_table = related_mgr.field.rel.to._meta.db_table # e.g., corpus_hashtag
            related_id = related_mgr.field.rel.to._meta.model._meta.model_name + "_id"  # e.g., hashtag_id
        elif hasattr(related_mgr, "related"):
            through_table = related_mgr.related.field.rel.through._meta.db_table # e.g., enhance_messageword
            related_table = related_mgr.related.model._meta.db_table # e.g., enhance_word
            related_id = related_mgr.related.model._meta.model_name + "_id"  # e.g., word_id

        final_query = "SELECT B.%s AS `%s`, count(*) AS `value` FROM (%s) AS A, `%s` AS B, `%s` AS C WHERE A.id=C.%s AND B.id=C.%s GROUP BY B.%s ORDER BY `value` DESC" %(fieldname, key, query, related_table, through_table, message_id, related_id, fieldname)
    return callback(final_query)


def group_messages_by_words_with_raw_query(query, callback):
    queryset = corpus_models.Message.objects.raw(query)
    #pattern = r'(?<=SELECT ).+(?= FROM])'
    #query = re.sub(pattern, "T5.`text` AS words, count(*) AS `value`", query)
    #pattern = r'(?<=SELECT ).+(?= FROM])'
    query = query.replace("`corpus_message`.`id`, `corpus_message`.`dataset_id`, `corpus_message`.`original_id`, `corpus_message`.`type_id`, `corpus_message`.`sender_id`, `corpus_message`.`time`, `corpus_message`.`language_id`, `corpus_message`.`sentiment`, `corpus_message`.`timezone_id`, `corpus_message`.`replied_to_count`, `corpus_message`.`shared_count`, `corpus_message`.`contains_hashtag`, `corpus_message`.`contains_url`, `corpus_message`.`contains_media`, `corpus_message`.`contains_mention`, `corpus_message`.`text`", "T5.`text` AS words, count(*) AS value")
    query += "GROUP BY `words` ORDER BY `value` DESC"

    return callback(query)

class DataTable(object):
    """
    This class knows how to calculate appropriate visualization data
    for a given pair of dimensions.
    """

    def __init__(self, primary_dimension, secondary_dimension=None):
        """
        Construct a DataTable for one or two dimensions.

        Dimensions may be string dimension keys or
        :class:`msgvis.apps.dimensions.models.CategoricalDimension` objects.

        :type primary_dimension: registry.models.CategoricalDimension
        :type secondary_dimension: registry.models.CategoricalDimension

        :return:
        """

        # Look up the dimensions if needed
        if isinstance(primary_dimension, basestring):
            primary_dimension = registry.get_dimension(primary_dimension)

        if secondary_dimension is not None and isinstance(secondary_dimension, basestring):
            secondary_dimension = registry.get_dimension(secondary_dimension)

        # a dirty way
        if secondary_dimension is not None and hasattr(secondary_dimension, 'key') and secondary_dimension.key == "groups":
            secondary_dimension = None

        self.primary_dimension = primary_dimension
        self.secondary_dimension = secondary_dimension

        self.mode = "default"

    def set_mode(self, mode):
        self.mode = mode

    def render(self, queryset, desired_primary_bins=None, desired_secondary_bins=None):
        """
        Given a set of messages (already filtered as necessary),
        calculate the data table.

        Optionally, a number of primary and secondary bins may be given.

        The result is a list of dictionaries. Each
        dictionary contains a key for each dimension
        and a value key for the count.
        """

        if not self.secondary_dimension:
            # If there is only one dimension, we should be able to fall back
            # on that dimension's group_by() implementation.
            queryset = self.primary_dimension.group_by(queryset,
                                                       grouping_key=self.primary_dimension.key,
                                                       bins=desired_primary_bins)

            return queryset.annotate(value=models.Count('id'))

        else:
            # Now it gets nasty...
            primary_group = self.primary_dimension.get_grouping_expression(queryset,
                                                                           bins=desired_primary_bins)

            secondary_group = self.secondary_dimension.get_grouping_expression(queryset,
                                                                               bins=desired_secondary_bins)

            if primary_group is None or secondary_group is None:
                # There is no data to group
                return queryset.values()

            queryset, internal_primary_key = self.primary_dimension.select_grouping_expression(
                queryset,
                primary_group)

            queryset, internal_secondary_key = self.secondary_dimension.select_grouping_expression(
                queryset,
                secondary_group)

            # Group the data
            queryset = queryset.values(internal_primary_key,
                                       internal_secondary_key)

            # Count the messages
            queryset = queryset.annotate(value=models.Count('id'))

            # We may need to remap some fields
            mapping = {}
            if internal_primary_key != self.primary_dimension.key:
                mapping[internal_primary_key] = self.primary_dimension.key
            if internal_secondary_key != self.secondary_dimension.key:
                mapping[internal_secondary_key] = self.secondary_dimension.key

            if len(mapping) > 0:
                return MappedValuesQuerySet.create_from(queryset, mapping)
            else:
                return queryset



    def render_others(self, queryset, domains, primary_flag, secondary_flag, desired_primary_bins=None, desired_secondary_bins=None):
        """
        Given a set of messages (already filtered as necessary),
        calculate the data table.

        Optionally, a number of primary and secondary bins may be given.

        The result is a list of dictionaries. Each
        dictionary contains a key for each dimension
        and a value key for the count.
        """

        # check if any of the dimensions is categorical
        if not primary_flag and not secondary_flag:
            return None

        if not self.secondary_dimension and self.primary_dimension.is_categorical() and primary_flag:
            # If there is only one dimension, we should be able to fall back
            # on that dimension's group_by() implementation.

            queryset = queryset.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
            domains[self.primary_dimension.key].append(u'Other ' + self.primary_dimension.name)

            return [{self.primary_dimension.key: u'Other ' + self.primary_dimension.name, 'value': queryset.count()}]

        elif self.secondary_dimension:

            # both dimensions are categorical
            if self.primary_dimension.is_categorical() and self.secondary_dimension.is_categorical():
                original_queryset = queryset
                others_results = []
                if primary_flag:
                    domains[self.primary_dimension.key].append(u'Other ' + self.primary_dimension.name)
                if secondary_flag:
                    domains[self.secondary_dimension.key].append(u'Other ' + self.secondary_dimension.name)

                # primary others x secondary others
                if primary_flag and secondary_flag:
                    queryset = queryset.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                    queryset = queryset.exclude(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))

                    others_results.append({self.primary_dimension.key: u'Other ' + self.primary_dimension.name,
                                           self.secondary_dimension.key: u'Other ' + self.secondary_dimension.name,
                                           'value': queryset.count()})

                # primary top ones x secondary others
                if secondary_flag:
                    queryset = original_queryset
                    queryset = queryset.filter(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                    queryset = queryset.exclude(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))

                    queryset = self.primary_dimension.group_by(queryset,
                                                                          grouping_key=self.primary_dimension.key)

                    queryset = queryset.annotate(value=models.Count('id'))
                    results = list(queryset)
                    for r in results:
                        r[self.secondary_dimension.key] = u'Other ' + self.secondary_dimension.name
                    others_results.extend(results)

                # primary others x secondary top ones
                if primary_flag:
                    queryset = original_queryset
                    queryset = queryset.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                    queryset = queryset.filter(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))

                    queryset = self.secondary_dimension.group_by(queryset,
                                                                            grouping_key=self.secondary_dimension.key)

                    queryset = queryset.annotate(value=models.Count('id'))
                    results = list(queryset)
                    for r in results:
                        r[self.primary_dimension.key] = u'Other ' + self.primary_dimension.name
                    others_results.extend(results)

                return others_results

            # primary categorical and secondary quantitative
            elif self.primary_dimension.is_categorical() and primary_flag and not self.secondary_dimension.is_categorical():
                queryset = queryset.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                domains[self.primary_dimension.key].append(u'Other ' + self.primary_dimension.name)
                queryset = self.secondary_dimension.group_by(queryset,
                                                                        grouping_key=self.secondary_dimension.key,
                                                                        bins=desired_secondary_bins)
                queryset = queryset.annotate(value=models.Count('id'))
                results = list(queryset)
                for r in results:
                    r[self.primary_dimension.key] = u'Other ' + self.primary_dimension.name
                return results

            # primary quantitative and secondary categorical
            elif not self.primary_dimension.is_categorical() and self.secondary_dimension.is_categorical() and secondary_flag:
                queryset = queryset.exclude(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))
                domains[self.secondary_dimension.key].append(u'Other ' + self.secondary_dimension.name)
                queryset = self.primary_dimension.group_by(queryset,
                                                                      grouping_key=self.primary_dimension.key,
                                                                      bins=desired_primary_bins)
                queryset = queryset.annotate(value=models.Count('id'))
                results = list(queryset)
                for r in results:
                    r[self.secondary_dimension.key] = u'Other ' + self.secondary_dimension.name
                return results


    def domain(self, dimension, queryset, filter=None, exclude=None, desired_bins=None):
        """Return the sorted levels in this dimension"""
        if filter is not None:
            queryset = dimension.filter(queryset, **filter)

        if exclude is not None:
            queryset = dimension.exclude(queryset, **exclude)

        domain = dimension.get_domain(queryset, bins=desired_bins)
        labels = dimension.get_domain_labels(domain)

        return domain, labels

    def groups_domain(self, dimension, queryset_all, group_querysets, desired_bins=None):
        """Return the sorted levels in the union of groups in this dimension"""
        if dimension.is_related_categorical():
            query = ""
            for idx, queryset in enumerate(group_querysets):
                if idx > 0:
                    query += " UNION "
                query += "(%s)" %(quote(str(queryset.query)))
            domain = group_messages_by_dimension_with_raw_query(query, dimension, fetchall)

        else:
            queryset = queryset_all
            domain = dimension.get_domain(queryset, bins=desired_bins)
        labels = dimension.get_domain_labels(domain)

        return domain, labels

    def filter_search_key(self, domain, labels, search_key):
        match_domain = []
        match_labels = []
        for i in range(len(domain)):
            level = domain[i]
            if level is not None and level.lower().find(search_key.lower()) != -1 :
                match_domain.append(level)

                if labels is not None:
                    match_labels.append(labels[i])

        return match_domain, match_labels

    def generate(self, dataset, filters=None, exclude=None, page_size=30, page=None, search_key=None, groups=None):
        """
        Generate a complete data group table response.

        This includes 'table', which provides the non-zero
        message frequency for each combination of primary and secondary dimension values,
        respecting the filters.

        It also includes 'domains', which provides, for both
        primary and secondary dimensions, the levels of the
        dimension irrespective of filters (except on those actual dimensions).
        """

        if (groups is None):
            queryset = dataset.message_set.all()

            # Filter out null time
            queryset = queryset.exclude(time__isnull=True)
            if dataset.start_time and dataset.end_time:
                range = dataset.end_time - dataset.start_time
                buffer = timedelta(seconds=range.total_seconds() * 0.1)
                queryset = queryset.filter(time__gte=dataset.start_time - buffer,
                                           time__lte=dataset.end_time + buffer)

            unfiltered_queryset = queryset

            # Filter the data (look for filters on the primary/secondary dimensions at the same time
            primary_filter = None
            secondary_filter = None
            if filters is not None:
                for filter in filters:
                    dimension = filter['dimension']
                    queryset = dimension.filter(queryset, **filter)

                    if dimension == self.primary_dimension:
                        primary_filter = filter
                    if dimension == self.secondary_dimension:
                        secondary_filter = filter

            primary_exclude = None
            secondary_exclude = None
            if exclude is not None:
                for exclude_filter in exclude:
                    dimension = exclude_filter['dimension']
                    queryset = dimension.exclude(queryset, **exclude_filter)

                    if dimension == self.primary_dimension:
                        primary_exclude = exclude_filter
                    if dimension == self.secondary_dimension:
                        secondary_exclude = exclude_filter

            domains = {}
            domain_labels = {}
            max_page = None
            queryset_for_others = None

            # flag is true if the dimension is categorical and has more than MAX_CATEGORICAL_LEVELS levels
            primary_flag = False
            secondary_flag = False

            # Include the domains for primary and (secondary) dimensions
            domain, labels = self.domain(self.primary_dimension,
                                         unfiltered_queryset,
                                         primary_filter, primary_exclude)

            # paging the first dimension, this is for the filter distribution
            if primary_filter is None and self.secondary_dimension is None and page is not None:

                if search_key is not None:
                    domain, labels = self.filter_search_key(domain, labels, search_key)
                start = (page - 1) * page_size
                end = min(start + page_size, len(domain))
                max_page = (len(domain) / page_size) + 1

                # no level left
                if len(domain) == 0 or start > len(domain):
                    return None

                domain = domain[start:end]
                if labels is not None:
                    labels = labels[start:end]

                queryset = queryset.filter(levels_or(self.primary_dimension.field_name, domain))
            else:
                if (self.mode == 'enable_others' or self.mode == 'omit_others') and \
                    self.primary_dimension.is_categorical() and len(domain) > MAX_CATEGORICAL_LEVELS:
                    primary_flag = True
                    domain = domain[:MAX_CATEGORICAL_LEVELS]

                    queryset_for_others = queryset
                    queryset = queryset.filter(levels_or(self.primary_dimension.field_name, domain))

                    if labels is not None:
                        labels = labels[:MAX_CATEGORICAL_LEVELS]

            domains[self.primary_dimension.key] = domain
            if labels is not None:
                domain_labels[self.primary_dimension.key] = labels

            if self.secondary_dimension:
                domain, labels = self.domain(self.secondary_dimension,
                                             unfiltered_queryset,
                                             secondary_filter, secondary_exclude)

                if (self.mode == 'enable_others' or self.mode == 'omit_others') and \
                    self.secondary_dimension.is_categorical() and \
                        len(domain) > MAX_CATEGORICAL_LEVELS:
                    secondary_flag = True
                    domain = domain[:MAX_CATEGORICAL_LEVELS]

                    if queryset_for_others is None:
                        queryset_for_others = queryset
                    queryset = queryset.filter(levels_or(self.secondary_dimension.field_name, domain))

                    if labels is not None:
                        labels = labels[:MAX_CATEGORICAL_LEVELS]


                domains[self.secondary_dimension.key] = domain
                if labels is not None:
                    domain_labels[self.secondary_dimension.key] = labels

            # Render a table
            table = self.render(queryset)

            if self.mode == "enable_others" and queryset_for_others is not None:
                # adding others to the results
                table_for_others = self.render_others(queryset_for_others, domains, primary_flag, secondary_flag)
                table = list(table)
                table.extend(table_for_others)

            results = {
                'table': table,
                'domains': domains,
                'domain_labels': domain_labels
            }
            if max_page is not None:
                results['max_page'] = max_page

        else:
            domains = {}
            domain_labels = {}
            max_page = None
            queryset_for_others = None

            # flag is true if the dimension is categorical and has more than MAX_CATEGORICAL_LEVELS levels
            primary_flag = False
            secondary_flag = False
            primary_filter = None
            secondary_filter = None
            primary_exclude = None
            secondary_exclude = None

            queryset = dataset.message_set.all()
            queryset = queryset.exclude(time__isnull=True)
            if dataset.start_time and dataset.end_time:
                range = dataset.end_time - dataset.start_time
                buffer = timedelta(seconds=range.total_seconds() * 0.1)
                queryset = queryset.filter(time__gte=dataset.start_time - buffer,
                                           time__lte=dataset.end_time + buffer)
            if filters is not None:
                for filter in filters:
                    dimension = filter['dimension']
                    queryset = dimension.filter(queryset, **filter)

                    if dimension == self.primary_dimension:
                        primary_filter = filter
                    if dimension == self.secondary_dimension:
                        secondary_filter = filter

            if exclude is not None:
                for exclude_filter in exclude:
                    dimension = exclude_filter['dimension']
                    queryset = dimension.exclude(queryset, **exclude_filter)

                    if dimension == self.primary_dimension:
                        primary_exclude = exclude_filter
                    if dimension == self.secondary_dimension:
                        secondary_exclude = exclude_filter

            queryset_all = queryset

            #queryset = corpus_models.Message.objects.none()
            group_querysets = []
            group_labels = []
            #message_list = set()


            for group in groups:
                group_obj = groups_models.Group.objects.get(id=group)
                group_labels.append(group_obj.name)
                queryset = group_obj.messages_online()


                # Filter out null time
                queryset = queryset.exclude(time__isnull=True)
                if dataset.start_time and dataset.end_time:
                    range = dataset.end_time - dataset.start_time
                    buffer = timedelta(seconds=range.total_seconds() * 0.1)
                    queryset = queryset.filter(time__gte=dataset.start_time - buffer,
                                               time__lte=dataset.end_time + buffer)

                unfiltered_queryset = queryset

                # Filter the data (look for filters on the primary/secondary dimensions at the same time

                if filters is not None:
                    for filter in filters:
                        dimension = filter['dimension']
                        queryset = dimension.filter(queryset, **filter)


                if exclude is not None:
                    for exclude_filter in exclude:
                        dimension = exclude_filter['dimension']
                        queryset = dimension.exclude(queryset, **exclude_filter)


                group_querysets.append(queryset)

#########################################################################################################################

            # deal with union distribution
            # This is due to union of queries in django does not work...
            # super ugly. Refactoring is required.


            # Include the domains for primary and (secondary) dimensions
            domain, labels = self.groups_domain(self.primary_dimension,
                                         queryset_all, group_querysets)

            # paging the first dimension, this is for the filter distribution
            if primary_filter is None and self.secondary_dimension is None and page is not None:

                if search_key is not None:
                    domain, labels = self.filter_search_key(domain, labels, search_key)
                start = (page - 1) * page_size
                end = min(start + page_size, len(domain))
                max_page = (len(domain) / page_size) + 1

                # no level left
                if len(domain) == 0 or start > len(domain):
                    return None

                domain = domain[start:end]
                if labels is not None:
                    labels = labels[start:end]

            else:
                if (self.mode == 'enable_others' or self.mode == 'omit_others') and \
                    self.primary_dimension.is_categorical() and len(domain) > MAX_CATEGORICAL_LEVELS:
                    primary_flag = True
                    domain = domain[:MAX_CATEGORICAL_LEVELS]

                    if labels is not None:
                        labels = labels[:MAX_CATEGORICAL_LEVELS]

            domains[self.primary_dimension.key] = domain
            if labels is not None:
                domain_labels[self.primary_dimension.key] = labels

            if self.secondary_dimension:
                domain, labels = self.groups_domain(self.secondary_dimension,
                                             queryset_all, group_querysets)

                if (self.mode == 'enable_others' or self.mode == 'omit_others') and \
                    self.secondary_dimension.is_categorical() and \
                        len(domain) > MAX_CATEGORICAL_LEVELS:
                    secondary_flag = True
                    domain = domain[:MAX_CATEGORICAL_LEVELS]

                    if labels is not None:
                        labels = labels[:MAX_CATEGORICAL_LEVELS]


                domains[self.secondary_dimension.key] = domain
                if labels is not None:
                    domain_labels[self.secondary_dimension.key] = labels
#########################################################################################################################

            group_tables = []
            for queryset in group_querysets:
                queryset_for_others = queryset
                if (self.mode == 'enable_others' or self.mode == 'omit_others') and \
                    self.primary_dimension.is_categorical():
                    queryset = queryset.filter(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                if self.secondary_dimension:
                    if (self.mode == 'enable_others' or self.mode == 'omit_others') and \
                    self.secondary_dimension.is_categorical():
                        if queryset_for_others is None:
                            queryset_for_others = queryset
                        queryset = queryset.filter(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))

                # Render a table
                if self.primary_dimension.key == "words":
                    table = group_messages_by_words_with_raw_query(quote(str(queryset.query)), fetchall_table)
                else:
                    table = self.render(queryset)

                if self.mode == "enable_others" and queryset_for_others is not None:
                    # adding others to the results
                    table_for_others = self.render_others(queryset_for_others, domains, primary_flag, secondary_flag)
                    table = list(table)
                    table.extend(table_for_others)

                group_tables.append(table)

            if self.secondary_dimension is None:
                final_table = []
                for idx, group_table in enumerate(group_tables):
                    for item in group_table:
                        item['groups'] = groups[idx]
                    final_table.extend(group_table)

                domains['groups'] = groups
                domain_labels['groups'] = group_labels
                results = {
                    'table': final_table,
                    'domains': domains,
                    'domain_labels': domain_labels
                }

            else:
                tables = []
                for idx, group_table in enumerate(group_tables):
                    tables.append({
                        'group_id': groups[idx],
                        'group_name': group_labels[idx],
                        'table': group_table
                    })
                results = {
                    'tables': tables,
                    'domains': domains,
                    'domain_labels': domain_labels
                }


            if max_page is not None:
                results['max_page'] = max_page

        return results
