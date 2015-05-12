"""
Helper functions for views.

"""
from functools import wraps
from django.contrib.auth.decorators import user_passes_test


def validate_form(request, form_cls, initial=None, instance=None, condition=True, **extra_kwargs):
    """
    Creates a form instance with/without data depending
    on whether page was POSTed. Returns the form instance.

    :param HttpRequest request: The request object.
    :param Form form_cls: The form class to be instantiated and validated.
    :param dict initial: Initial values for form fields.
    :param type instance: An initial model instance for ModelForms.
    :param bool condition: A boolean indicating whether this form should be validated
        from POST. Useful if there are multiple forms on the page::

            form = validate_form(request, MyForm, condition=('myformsubmit' in request.POST))

    :param extra_kwargs: Any extra kwargs passed to the form constructor.

    :returns: The validated form class instance, after calling ``full_clean()``.
    """
    kwargs = {}
    if initial is not None:
        kwargs['initial'] = initial
    if instance is not None:
        kwargs['instance'] = instance
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    if request.method == 'POST' and condition:
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
