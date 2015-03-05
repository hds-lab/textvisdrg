from django.db import models
from django.db.models import query


class MappedValuesQuerySet(query.ValuesQuerySet):
    """
    A special ValuesQuerySet that can re-map the dictionary keys
    while they are bing iterated over.

    .. code-block:: python

        valuesQuerySet = queryset.values('some__ugly__field__expression')
        mapped = MappedQuerySet.create_from(valuesQuerySet, {
            'some__ugly__field__expression': 'nice_expression'
        })
        mapped[0]
        # { 'nice_expression': 5 }

    """

    def __init__(self, *args, **kwargs):
        super(MappedValuesQuerySet, self).__init__(*args, **kwargs)
        self.field_map = kwargs.get('field_map', {})

    @classmethod
    def create_from(cls, values_query_set, field_map):
        """Create a MappedValueQuerySet with a field name mapping dictionary."""
        return values_query_set._clone(cls, field_map=field_map)

    def _clone(self, klass=None, setup=False, **kwargs):
        c = super(MappedValuesQuerySet, self)._clone(klass, setup, **kwargs)
        c.field_map = self.field_map
        return c

    def iterator(self):
        # Purge any extra columns that haven't been explicitly asked for
        extra_names = list(self.query.extra_select)
        field_names = self.field_names
        aggregate_names = list(self.query.aggregate_select)

        names = extra_names + field_names + aggregate_names

        # Remap the fields, but fall back on regular name
        names = [self.field_map.get(name, name) for name in names]

        for row in self.query.get_compiler(self.db).results_iter():
            yield dict(zip(names, row))


class CharsetFieldMixin(object):
    def __init__(self, character_set=None, collation=None, **kwargs):
        self.charset_create_args = {}

        if character_set is not None:
            self.character_set = character_set
            self.charset_create_args['character_set'] = character_set

        if collation is not None:
            self.collation = collation
            self.charset_create_args['collation'] = collation

        super(CharsetFieldMixin, self).__init__(**kwargs)

    def db_parameters(self, connection):
        params = super(CharsetFieldMixin, self).db_parameters(connection)
        if params and 'type' in params \
            and connection.vendor == 'mysql' \
            and (self.character_set is not None or self.collation is not None):

            params['type'] = '%s CHARACTER SET %s COLLATE %s' % (params['type'], self.character_set, self.collation)

        return params

    def deconstruct(self):
        name, path, args, kwargs = super(CharsetFieldMixin, self).deconstruct()
        kwargs.update(self.charset_create_args)
        return name, path, args, kwargs


class Utf8TextField(CharsetFieldMixin, models.TextField):
    character_set = 'utf8mb4'
    collation = 'utf8mb4_general_ci'


class Utf8CharField(CharsetFieldMixin, models.CharField):
    character_set = 'utf8mb4'
    collation = 'utf8mb4_general_ci'
