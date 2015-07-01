import functools
from time import time
import operator
from django.db import connection
from django.http.response import HttpResponse
from django.utils.html import escapejs


STATS_KEY = '_performancestatsmiddleware'


class PerformanceStatsMiddleware(object):
    """
    Middleware class for printing out performance stats of each
    request to the shell and browser console.

    Place this first in your middleware classes::

        MIDDLEWARE_CLASSES = (
            'dwtools3.django.helpers.middleware.PerformanceStatsMiddleware',
        ) + MIDDLEWARE_CLASSES
    """
    def process_request(self, request):
        setattr(request, STATS_KEY, {
            'start': time(),
            'view_start': None,
        })

    def process_view(self, request, view_func, view_args, view_kwargs):
        stats = getattr(request, STATS_KEY)
        stats['view_start'] = time()
        stats['middleware_db_queries'] = len(connection.queries)
        stats['middleware_db_time'] = functools.reduce(operator.add, (float(q['time']) for q in connection.queries))
        return None

    def process_response(self, request, response):
        stats = getattr(request, STATS_KEY)
        if not stats['view_start']:
            return response

        stats['end'] = time()
        stats['total_time'] = stats['end'] - stats['start']
        stats['db_queries'] = len(connection.queries)
        stats['db_time'] = functools.reduce(operator.add, (float(q['time']) for q in connection.queries))
        stats['python_time'] = stats['total_time'] - stats['db_time']

        stats['middleware_total_time'] = stats['end'] - stats['view_start']
        stats['middleware_python_time'] = stats['middleware_total_time'] - stats['middleware_db_time']

        stats['view_total_time'] = stats['view_start'] - stats['start']
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
