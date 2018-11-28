from collections import namedtuple

from django.test import TestCase

from ..helpers.middleware import TranslateProxyRemoteAddrMiddleware


class DjangoHelpersMiddlewareTestCase(TestCase):
    def test_translate_proxy_remote_addr_middleware(self):
        TESTS = [
            ('1.2.3.4', '1.2.3.4'),
            ('1.2.3.4,5.6.7.8', '1.2.3.4'),
            (',1.2.3.4', '1.2.3.4'),
            ('unknown,1.2.3.4', '1.2.3.4'),
            (',unknown', ''),
            ('unknown,unknown', ''),
            ('unknown', ''),
            ('', ''),
        ]

        def get_response(request):
            return request.META['REMOTE_ADDR']

        Request = namedtuple('Request', ['META'])

        request = Request(META={'REMOTE_ADDR': '1.2.3.4'})
        result = TranslateProxyRemoteAddrMiddleware(get_response)(request)
        self.assertEqual(result, '1.2.3.4')

        for header, expected in TESTS:
            request = Request(META={'HTTP_X_FORWARDED_FOR': header})
            result = TranslateProxyRemoteAddrMiddleware(get_response)(request)
            self.assertEqual(result, expected)
