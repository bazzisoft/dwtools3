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

        url(r'^500/$', template_view('500.html', context=Context())),
    """
    def view_func(request):
        return render(request, *args, **kwargs)

    return view_func
