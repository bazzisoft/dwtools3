"""
Helper functions for views.

"""
from functools import wraps
from django.contrib.auth.decorators import user_passes_test


# TODO: Support multiple forms: Add keyword arg to specify a POST variable that must be set in order to validate the form
def validate_form(request, form_cls, prefix=None, initial=None, instance=None, **extra_kwargs):
    """
    Creates a form instance with/without data depending
    on whether page was POSTed. Returns the form instance.
    """
    kwargs = dict(prefix=prefix, initial=initial)
    if instance is not None:
        kwargs['instance'] = instance
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    if request.method == 'POST':
        form = form_cls(data=request.POST, files=(request.FILES if len(request.FILES) else None), **kwargs)
    else:
        form = form_cls(**kwargs)

    form.full_clean()
    return form


def set_page_meta(request, **kwargs):
    """
    Creates a dict ``request.meta`` and populates it
    with the values of kwargs.

    Standard keys to use include title, keywords, description & menu.
    """
    if not hasattr(request, 'meta'):
        request.meta = {}

    canonical = kwargs.get('canonical', None)
    if canonical and not canonical.startswith('http'):
        kwargs['canonical'] = request.build_absolute_uri(canonical)

    request.meta.update(kwargs)


def meta(**kwargs):
    """
    Decorator that can be used to wrap views and have
    them provide page metadata such as title, description,
    canonical, etc.
    Uses ``set_page_meta``.

    Eg. ::

        @meta(title='My Page', menu='mypage')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        metadata = kwargs

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            set_page_meta(request, **metadata)
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def superuser_required(view_func):
    """
    Decorator that ensures a superuser is logged in.
    """
    return user_passes_test(lambda u: u.is_superuser)(view_func)
