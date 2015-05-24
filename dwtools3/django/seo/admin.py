from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.utils.html import escape
from .models import MetaTags, Redirect, normalize_url


def get_seo_metatags_admin_url(obj_url):
    """
    Returns a URL pointing to an admin add/edit page
    for the SEO meta tags of the given URL.
    """
    obj_url = normalize_url(obj_url)
    return reverse('seo_metatags_admin_redirect') + '?url=' + urlquote(obj_url)


def create_seo_metatags_admin_list_column(get_url_for_instance_fn=None):
    """
    Helper function for linking to an SEO page for a model instance,
    from the ``ModelAdmin`` changelist page.

    See: ``__init__.py`` documentation.
    """
    if get_url_for_instance_fn is None:
        get_url_for_instance_fn = lambda obj: obj.get_absolute_url()

    def _seo_link(self, obj):
        url = get_seo_metatags_admin_url(get_url_for_instance_fn(obj))
        return '<a href="{}">SEO</a>'.format(escape(url))
    _seo_link.short_description = ''
    _seo_link.allow_tags = True

    return _seo_link


@admin.register(MetaTags)
class MetaTagsAdmin(admin.ModelAdmin):
    # List
    list_display = ('url', 'title', 'description', 'keywords', 'footer_text')
    list_display_links = ('url',)
    search_fields = ('url', 'title',)
    ordering = ('url',)


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    # List
    list_display = ('url', 'target_url', 'is_permanent', 'with_query_string')
    list_display_links = ('url',)
    search_fields = ('url', 'target_url',)
    ordering = ('url',)
