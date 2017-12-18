"""
Common views.
"""
from django.shortcuts import redirect, render


def redirect_view(to, *args, **kwargs):
    """
    Returns a view function for redirecting to an arbitrary URL.
    """
    def view_func(request):
        return redirect(to, *args, **kwargs)

    return view_func


def template_view(template, *args, **kwargs):
    """
    Returns a view function for rendering a simple template via
    ``django.shortcuts.render()``.

    Example usage::

        url(r'^500/$', template_view('500.html', no_context=True)),
    """
    no_context = kwargs.pop('no_context', False)
    def view_func(request):
        req = None if no_context else request
        return render(req, template, *args, **kwargs)

    return view_func
