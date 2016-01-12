from django.shortcuts import redirect
from ...http import modify_url_query_string
from .models import Redirect, normalize_url


class SEORedirectMiddleware(object):
    """
    Intercepts 404 errors and checks the database for any defined
    redirecs that match the current request path.
    """
    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        try:
            r = Redirect.objects.get(url=normalize_url(request.path))
        except Redirect.DoesNotExist:
            return response

        to = r.target_url
        kwargs = dict(permanent=r.is_permanent)

        if r.with_query_string:
            to = modify_url_query_string(to, replace=request.GET.dict())

        return redirect(to, **kwargs)
