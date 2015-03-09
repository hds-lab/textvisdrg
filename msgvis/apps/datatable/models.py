from django.db import models
from django.db.models import Q
import operator

from msgvis.apps.base.models import MappedValuesQuerySet
from msgvis.apps.corpus import models as corpus_models
from msgvis.apps.dimensions import registry

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

        # Type checking
        queryset = find_messages(queryset)

        # Filter out null time
        queryset = queryset.exclude(time__isnull=True)

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



    def render_others(self, queryset_for_others, domains, desired_primary_bins=None, desired_secondary_bins=None):
        """
        Given a set of messages (already filtered as necessary),
        calculate the data table.

        Optionally, a number of primary and secondary bins may be given.

        The result is a list of dictionaries. Each
        dictionary contains a key for each dimension
        and a value key for the count.
        """

        # check if any of the dimensions is categorical
        if not self.secondary_dimension and not self.primary_dimension.is_categorical():
            return None

        # Type checking
        queryset_for_others = find_messages(queryset_for_others)

        # Filter out null time
        queryset_for_others = queryset_for_others.exclude(time__isnull=True)

        if not self.secondary_dimension and self.primary_dimension.is_categorical():
            # If there is only one dimension, we should be able to fall back
            # on that dimension's group_by() implementation.

            queryset_for_others = queryset_for_others.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
            domains[self.primary_dimension.key].append(u'Other ' + self.primary_dimension.key)

            return [{self.primary_dimension.key: u'Other ' + self.primary_dimension.key, 'value': queryset_for_others.count()}]

        elif self.secondary_dimension:

            # both dimensions are categorical
            if self.primary_dimension.is_categorical() and self.secondary_dimension.is_categorical():
                original_queryset = queryset_for_others
                others_results = []
                domains[self.primary_dimension.key].append(u'Other ' + self.primary_dimension.key)
                domains[self.secondary_dimension.key].append(u'Other ' + self.secondary_dimension.key)

                # primary others x secondary others
                queryset_for_others = queryset_for_others.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                queryset_for_others = queryset_for_others.exclude(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))

                others_results.append({self.primary_dimension.key: u'Other ' + self.primary_dimension.key,
                                       self.secondary_dimension.key: u'Other ' + self.secondary_dimension.key,
                                       'value': queryset_for_others.count()})

                # primary top ones x secondary others
                queryset_for_others = original_queryset
                queryset_for_others = queryset_for_others.filter(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                queryset_for_others = queryset_for_others.exclude(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))

                queryset_for_others = self.primary_dimension.group_by(queryset_for_others,
                                                                      grouping_key=self.primary_dimension.key)

                queryset_for_others = queryset_for_others.annotate(value=models.Count('id'))
                results = list(queryset_for_others)
                for r in results:
                    r[self.secondary_dimension.key] = u'Other ' + self.secondary_dimension.key
                others_results.extend(results)

                # primary others x secondary top ones
                queryset_for_others = original_queryset
                queryset_for_others = queryset_for_others.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                queryset_for_others = queryset_for_others.filter(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))

                queryset_for_others = self.secondary_dimension.group_by(queryset_for_others,
                                                                        grouping_key=self.secondary_dimension.key)

                queryset_for_others = queryset_for_others.annotate(value=models.Count('id'))
                results = list(queryset_for_others)
                for r in results:
                    r[self.primary_dimension.key] = u'Other ' + self.primary_dimension.key
                others_results.extend(results)

                return others_results

            # primary categorical and secondary quantitative
            elif self.primary_dimension.is_categorical() and not self.secondary_dimension.is_categorical():
                queryset_for_others = queryset_for_others.exclude(levels_or(self.primary_dimension.field_name, domains[self.primary_dimension.key]))
                domains[self.primary_dimension.key].append(u'Other ' + self.primary_dimension.key)
                queryset_for_others = self.secondary_dimension.group_by(queryset_for_others,
                                                                        grouping_key=self.secondary_dimension.key,
                                                                        bins=desired_secondary_bins)
                queryset_for_others = queryset_for_others.annotate(value=models.Count('id'))
                results = list(queryset_for_others)
                for r in results:
                    r[self.primary_dimension.key] = u'Other ' + self.primary_dimension.key
                return results

            # primary quantitative and secondary categorical
            elif not self.primary_dimension.is_categorical() and self.secondary_dimension.is_categorical():
                queryset_for_others = queryset_for_others.exclude(levels_or(self.secondary_dimension.field_name, domains[self.secondary_dimension.key]))
                domains[self.secondary_dimension.key].append(u'Other ' + self.secondary_dimension.key)
                queryset_for_others = self.primary_dimension.group_by(queryset_for_others,
                                                                      grouping_key=self.primary_dimension.key,
                                                                      bins=desired_primary_bins)
                queryset_for_others = queryset_for_others.annotate(value=models.Count('id'))
                results = list(queryset_for_others)
                for r in results:
                    r[self.secondary_dimension.key] = u'Other ' + self.secondary_dimension.key
                return results


    def domain(self, dimension, queryset, filter=None, exclude=None, desired_bins=None):
        """Return the sorted levels in this dimension"""
        if filter is not None:
            queryset = dimension.filter(queryset, **filter)

        if exclude is not None:
            queryset = dimension.exclude(queryset, **exclude)

        queryset = queryset.exclude(time__isnull=True)
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

    def generate(self, dataset, filters=None, exclude=None, page_size=30, page=None, search_key=None):
        """
        Generate a complete data table response.

        This includes 'table', which provides the non-zero
        message frequency for each combination of primary and secondary dimension values,
        respecting the filters.

        It also includes 'domains', which provides, for both
        primary and secondary dimensions, the levels of the
        dimension irrespective of filters (except on those actual dimensions).
        """

        queryset = dataset.message_set.all()

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


        table = None
        domains = {}
        domain_labels = {}
        max_page = None
        queryset_for_others = None

        # Include the domains for primary and (secondary) dimensions
        domain, labels = self.domain(self.primary_dimension,
                                     dataset.message_set.all(),
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
            if self.mode == 'enable_others' and self.primary_dimension.is_categorical() and len(domain) > MAX_CATEGORICAL_LEVELS:
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
                                         dataset.message_set.all(),
                                         secondary_filter, secondary_exclude)

            if self.mode == 'enable_others' and self.secondary_dimension.is_categorical() and len(domain) > MAX_CATEGORICAL_LEVELS:
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

        if self.mode == "enable_others" and (self.primary_dimension.is_categorical() or
                                            (self.secondary_dimension and self.secondary_dimension.is_categorical())):
            # adding others to the results
            table_for_others = self.render_others(queryset_for_others, domains)
            table = list(table)
            table.extend(table_for_others)

        results = {
            'table': table,
            'domains': domains,
            'domain_labels': domain_labels
        }
        if max_page is not None:
            results['max_page'] = max_page

        return results
