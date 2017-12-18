"""
Provides basic SEO functionality for dynamic meta tag management
and dynamic redirects via the admin. The functionality is mapped
to the site's pages via relative URLs.


Installation
------------
Django settings::

    INSTALLED_APPS = [
        'dwtools3.django.seo',
    ]

    # If you wish to use the dynamic redirects functionality
    MIDDLEWARE = [
        'dwtools3.django.seo.middleware.SEORedirectMiddleware',
    ]

    # If you wish to use the dynamic meta tags functionality
    TEMPLATES = [
        {
            'OPTIONS': {
                'context_processors': [
                    'dwtools3.django.seo.context_processors.metatags',
                ],
            },
        },
    ]


``urls.py``::

    # If you wish to create direct links from model admin pages to the
    # SEO meta tags edit page for those models
    urlpatterns = [
        url(r'^', include('dwtools3.django.seo.urls')),
    ]


Usage
-----

Redirects
^^^^^^^^^

Install the app and the middleware. Then simply define URLs and Target URLs
in the admin interface for the SEO Redirects model.


Meta Tags
^^^^^^^^^

Install the app and the context processor. The context processor provided by
the app doesn't add any variables, rather adds or overrides a ``request.meta``
dict with any SEO fields defined in the database for the current page's URL.

Define the URLs and meta tags via ther admin interface for SEO Meta Tags.

In your templates, use the following::

    {{ request.meta.title }}
    {{ request.meta.keywords }}
    {{ request.meta.description }}
    {{ request.meta.footer_text }}


Direct linking Meta Tags add/edit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the above, add the SEO app's ``urls.py`` entries to your URLconf.
This defines a view that will redirect to the admin Meta Tags add/edit page
for a given URL.

You may then do the following::

    from dwtools3.django.seo.admin import get_seo_metatags_admin_url, \\
        create_seo_metatags_admin_list_column

    # Easy way
    list_display = ('list_seo', ...)
    list_seo = create_seo_metatags_admin_list_column(lambda obj: obj.get_absolute_url())

    # Flexible way
    list_display = ('list_ops', ...)

    def list_ops(self, obj):
        seo_url = get_seo_metatags_admin_url(obj.get_absolute_url())
        return mark_safe('''-&nbsp;<a href="{}">SEO</a><br />'''.format(seo_url))
    list_ops.short_description = ''
"""
