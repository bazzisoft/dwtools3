import functools
from time import time
import operator
from django.db import connection
from django.http.response import HttpResponse
from django.utils.html import escapejs


class TranslateProxyRemoteAddrMiddleware(object):
    """
    Proxy servers (eg. nginx -> gunicorn) tend to override
    the REMOTE_ADDR header.

    This middleware translates the HTTP_X_FORWARDED_FOR header
    back to REMOTE_ADDR for getting the end-user's IP.

    To install simply add it to your middleware tuple after
    CommonMiddleware::

        MIDDLEWARE_CLASSES = (
            ...
            'dwtools3.django.helpers.middleware.TranslateProxyRemoteAddrMiddleware',
        )
    """
    def process_request(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
            request.META['REMOTE_ADDR'] = ip


class PerformanceStatsMiddleware(object):
    """
    Middleware class for printing out performance stats of each
    request to the shell and browser console.

    Place this first in your middleware classes::

        MIDDLEWARE_CLASSES = (
            'dwtools3.django.helpers.middleware.PerformanceStatsMiddleware',
        ) + MIDDLEWARE_CLASSES

    If you have "debug only" middleware that shouldn't be measured, place it
    before ``PerformanceStatsMiddleware``.
    """
    STATS_KEY = '_performancestatsmiddleware'

    def process_request(self, request):
        setattr(request, self.STATS_KEY, {
            'start': time(),
            'view_start': None,
        })

    def process_view(self, request, view_func, view_args, view_kwargs):
        stats = getattr(request, self.STATS_KEY)
        stats['view_start'] = time()
        stats['middleware_db_queries'] = len(connection.queries)
        stats['middleware_db_time'] = functools.reduce(operator.add, (float(q['time']) for q in connection.queries), 0.0)
        return None

    def process_response(self, request, response):
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
