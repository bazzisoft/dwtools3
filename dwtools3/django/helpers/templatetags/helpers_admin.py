from django import template
from django.apps import apps


register = template.Library()


@register.inclusion_tag('helpers/admin/breadcrumbs.html')
def render_breadcrumbs(title, app=None, model=None, instance=None, is_popup=False):
    """
    Renders the Django admin breadcrumb trail.

    eg::

            {% render_breadcumbs 'My Page' %}
            {% render_breadcumbs 'My Page' app='auth' %}
            {% render_breadcumbs 'My Page' model=User %}
            {% render_breadcumbs 'My Page' instance=request.user %}
    """
    if instance:
        model = type(instance)

    if model:
        app = model._meta.app_label

    if app:
        app = apps.get_app_config(app)

    return {
        'title': title,
        'app_label': app.label if app else None,
        'app_name': app.verbose_name if app else None,
        'model_name': model._meta.verbose_name_plural if model else None,
        'model_urlname': 'admin:{}_{}_changelist'.format(app.label, model._meta.model_name) if model else None,
        'instance': instance,
        'instance_urlname': 'admin:{}_{}_change'.format(app.label, model._meta.model_name) if instance else None,
        'is_popup': is_popup,
    }
