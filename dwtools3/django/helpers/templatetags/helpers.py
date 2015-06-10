from django import template


register = template.Library()


@register.filter
def lookup(dct, key):
    return dct.get(key)
