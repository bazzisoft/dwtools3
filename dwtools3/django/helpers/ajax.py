"""
Decorators and exceptions for handling Ajax views with JSON input and output.
"""
import enum
from functools import wraps
import json
import time

from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponseBadRequest, JsonResponse, \
    HttpResponseForbidden, HttpResponse
from django.utils.http import http_date
from django.views.decorators.csrf import ensure_csrf_cookie


class AjaxBadRequest(Exception):
    """
    Raise from your Ajax view to return a ``HttpResponseBadRequest``.
    """


class AjaxPermissionDenied(Exception):
    """
    Raise from your Ajax view to return a ``HttpResponseForbidden``.
    """


def ajax(methods, login_required=False, expires_in=None, encoder=DjangoJSONEncoder):
    """
    Decorator to pre- and post-process an Ajax view with JSON inputs and outputs.

    The decorator decodes ``request.body`` as JSON and provides it to your view
    using the keyword argument ``jsondata``. It then encodes the response object
    as JSON before returning it.

    You may raise ``AjaxBadRequest()`` or ``AjaxPermissionDenied()`` from your
    view to short-circuit processing and abort.

    :param str/list method: A single or list of HTTP methods supported by this endpoint.
    :param bool login_required: True is a ``request.user.is_authenticated()`` check
        should be made before the view runs.
    :param int expires_in: If none, no caching headers are sent. If positive/negative,
        the Expires HTTP header is set for the given number of secs forward/backward.

    Example::

        @ajax(['POST'], login_required=True)
        def my_view(request, jsondata=None):
            if jsondata['id'] == 1:
                return {'success': True}
            else:
                return {'success': False}

    """
    assert isinstance(methods, (str, tuple, list)), \
        'First argument to @ajax must be a list of supported HTTP methods.'
    methods = tuple(methods) if isinstance(methods, str) else methods

    def decorator(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return HttpResponseBadRequest('Method {} not supported.'.format(request.method))

            if login_required and not request.user.is_authenticated():
                return HttpResponseForbidden('Permission denied.')

            if request.body:
                try:
                    kwargs = dict(kwargs, jsondata=json.loads(request.body.decode('utf-8')))
                except ValueError:
                    return HttpResponseBadRequest('Invalid JSON in request body.')

            try:
                ret = fn(request, *args, **kwargs)
            except AjaxBadRequest as e:
                return HttpResponseBadRequest(str(e))
            except AjaxPermissionDenied as e:
                return HttpResponseForbidden(str(e) or 'Permission denied.')

            if isinstance(ret, HttpResponse):
                response = ret
            else:
                response = JsonResponse(data=ret, safe=False, encoder=encoder)

            if expires_in:
                response['Expires'] = http_date(time.time() + expires_in)
                response['Cache-Control'] = 'private, max-age={}'.format(expires_in)

            return response

        return ensure_csrf_cookie(wrapper)
    return decorator


class DjangoJSONEncoderWithEnum(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types, and enums.
    """
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, enum.Enum):
            return str(o)
        else:
            return super().default(o)


def cors(origins):
    """
    Decorator to send CORS access control headers for the whitelisted origins specified.

    :param origins list: List of origins in the form: ``['https://othersite.com']``
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            response = fn(request, *args, **kwargs)
            if request.META.get('HTTP_ORIGIN') and request.META.get('HTTP_ORIGIN') in origins:
                response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
            return response
        return wrapper
    return decorator
