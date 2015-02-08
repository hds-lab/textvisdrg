# This file is a fix for this issue with django-compressor
# https://github.com/django-compressor/django-compressor/issues/226

# This is a less filter that explicitly calls CssAbsoluteFilter.

# After adding the relative-urls flag to the lessc command,
# it appears to be unnecessary but I'm leaving it here in case
# we need it later for other deployment setups.

from compressor.filters.base import CompilerFilter
from compressor.filters.css_default import CssAbsoluteFilter

from django.conf import settings


class LessFilter(CompilerFilter):
    def __init__(self, content, attrs, **kwargs):
        super(LessFilter, self).__init__(content, command=settings.BIN_LESSC_COMMAND, **kwargs)

    def input(self, **kwargs):
        content = super(LessFilter, self).input(**kwargs)
        return CssAbsoluteFilter(content).input(**kwargs)

