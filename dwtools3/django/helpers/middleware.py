import functools
from time import time
import operator
from django.db import connection
from django.http.response import HttpResponse
from django.utils.html import escapejs


def TranslateProxyRemoteAddrMiddleware(get_response):
    """
    Proxy servers (eg. nginx -> gunicorn) tend to override
    the REMOTE_ADDR header.

    This middleware translates the HTTP_X_FORWARDED_FOR header
    back to REMOTE_ADDR for getting the end-user's IP.

    To install simply add it to your middleware tuple after
    CommonMiddleware::

        MIDDLEWARE = [
            ...
            'dwtools3.django.helpers.middleware.TranslateProxyRemoteAddrMiddleware',
        ]
    """
    def middleware(request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            fwd_ip = ''
            for ip in request.META['HTTP_X_FORWARDED_FOR'].split(','):
                ip = ip.strip()
                if ip and ip != 'unknown':
                    fwd_ip = ip
                    break
            request.META['REMOTE_ADDR'] = fwd_ip

        return get_response(request)
    return middleware


class PerformanceStatsMiddleware:
    """
    Middleware class for printing out performance stats of each
    request to the shell and browser console.

    Place this first in your middleware classes::

        MIDDLEWARE = [
            'dwtools3.django.helpers.middleware.PerformanceStatsMiddleware',
        ] + MIDDLEWARE

    If you have "debug only" middleware that shouldn't be measured, place it
    before ``PerformanceStatsMiddleware``.
    """
    STATS_KEY = '_performancestatsmiddleware'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, self.STATS_KEY, {
            'start': time(),
            'view_start': None,
        })

        response = self.get_response(request)

        stats = getattr(request, self.STATS_KEY, None)
        if stats is None or not stats['view_start']:
            return response

        stats['end'] = time()
        stats['total_time'] = stats['end'] - stats['start']
        stats['db_queries'] = len(connection.queries)
        stats['db_time'] = functools.reduce(operator.add, (float(q['time']) for q in connection.queries), 0.0)
        stats['python_time'] = stats['total_time'] - stats['db_time']

        stats['middleware_total_time'] = stats['view_start'] - stats['start']
        stats['middleware_python_time'] = stats['middleware_total_time'] - stats['middleware_db_time']

        stats['view_total_time'] = stats['end'] - stats['view_start']
        stats['view_db_queries'] = stats['db_queries'] - stats['middleware_db_queries']
        stats['view_db_time'] = stats['db_time'] - stats['middleware_db_time']
        stats['view_python_time'] = stats['view_total_time'] - stats['view_db_time']

        formatted = []
        formatted.append('     STATS: total:{:4.0f}ms,  python:{:4.0f}ms,  db:{:4.0f}ms,  queries:{:3d}'
                         .format(stats['total_time'] * 1000.0, stats['python_time'] * 1000.0,
                                 stats['db_time'] * 1000.0, stats['db_queries']))
        formatted.append('MIDDLEWARE: total:{:4.0f}ms,  python:{:4.0f}ms,  db:{:4.0f}ms,  queries:{:3d}'
                         .format(stats['middleware_total_time'] * 1000.0, stats['middleware_python_time'] * 1000.0,
                                 stats['middleware_db_time'] * 1000.0, stats['middleware_db_queries']))
        formatted.append('      VIEW: total:{:4.0f}ms,  python:{:4.0f}ms,  db:{:4.0f}ms,  queries:{:3d}'
                         .format(stats['view_total_time'] * 1000.0, stats['view_python_time'] * 1000.0,
                                 stats['view_db_time'] * 1000.0, stats['view_db_queries']))
        formatted = '\n'.join(formatted)

        print('')
        print(formatted)

        if (type(response) is HttpResponse and response['Content-Type'].startswith('text/html')
                and not response.get('Content-Disposition')):
            newcontent = ('''<script>console.log(\'{}\');</script>\n</body>'''.format(escapejs(formatted)))
            response.content = response.content.replace(b'</body>', newcontent.encode('utf-8'))

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        stats = getattr(request, self.STATS_KEY)
        stats['view_start'] = time()
        stats['middleware_db_queries'] = len(connection.queries)
        stats['middleware_db_time'] = functools.reduce(operator.add, (float(q['time']) for q in connection.queries), 0.0)
        return None
