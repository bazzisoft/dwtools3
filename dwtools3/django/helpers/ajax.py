"""
Decorators and exceptions for handling Ajax views with JSON input and output.
"""
import json
from functools import wraps
from django.http.response import HttpResponseBadRequest, JsonResponse, \
    HttpResponseForbidden
from django.views.decorators.csrf import ensure_csrf_cookie


class AjaxBadRequest(Exception):
    """
    Raise from your Ajax view to return a ``HttpResponseBadRequest``.
    """
    pass


class AjaxPermissionDenied(Exception):
    """
    Raise from your Ajax view to return a ``HttpResponseForbidden``.
    """
    pass


def ajax(methods, login_required=False):
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

    Example::

        @ajax(['POST'], login_required=True)
        def my_view(request, jsondata=None):
            if jsondata['id'] == 1:
                return {'success': True}
            else:
                return {'success': False}

    """
    assert isinstance(methods, (str, tuple, list)), 'First argument to @ajax must be a list of supported HTTP methods.'
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

            return JsonResponse(data=ret, safe=False)

        return ensure_csrf_cookie(wrapper)
    return decorator
