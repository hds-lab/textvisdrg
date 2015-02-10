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
