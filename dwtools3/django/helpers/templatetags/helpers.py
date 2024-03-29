from django import template
from django.shortcuts import resolve_url


register = template.Library()


@register.filter
def lookup(dct, key):
    return dct.get(key)


@register.simple_tag(takes_context=True)
def absolute_url(context, url, *args, **kwargs):
    url = resolve_url(url, *args, **kwargs)
    return context["request"].build_absolute_uri(url)
