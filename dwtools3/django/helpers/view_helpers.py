# pylint: disable=redefined-builtin
"""
Helper functions for views.
"""
import operator
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from django.template import engines, loader
from django.template.base import TemplateSyntaxError


def render_template_to_string(template=None, vars=None, request=None, template_string=None):
    """
    Renders a template file or template string to a rendered string.

    :param str template: The path & name of the template to render.
    :param dict vars: Extra template variables to push onto the context.
    :param HttpRequest request: The request object. May be None to exclude request context.
    :param str template: String content to use as the template.
    """
    assert operator.xor(bool(template), bool(template_string)), \
        'Exactly one of template or template_string must be specified.'

    if template_string:
        chain = []
        for engine in engines.all():
            try:
                template_obj = engine.from_string(template_string)
            except TemplateSyntaxError as e:
                chain.append(e)

        if chain:
            raise TemplateSyntaxError(template_string, chain=chain)

        output = template_obj.render(vars, request)
    else:
        output = loader.render_to_string(template, vars, request=request)

    return output


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
        form = form_cls(
            data=request.POST, files=(request.FILES if request.FILES else None), **kwargs)
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


def clear_django_messages(request):
    """
    Clears any pending messages in ``django.contrib.messages``.
    """
    # Iterate over the messages to clear them
    list(messages.get_messages(request))


def get_model_or_404(getter_fn, pk):
    """
    Calls ``getter_fn`` with ``pk`` and returns the resulting object.
    If ``ObjectDoesNotExist`` is caught, raises Http404
    """
    try:
        return getter_fn(pk)
    except ObjectDoesNotExist:
        raise Http404
