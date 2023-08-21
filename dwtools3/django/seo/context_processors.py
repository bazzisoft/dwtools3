from .models import MetaTags, normalize_url


def metatags(request):
    """
    Updates the request object to include any DB-based
    SEO meta tags.

    This happens the first time any template is rendered with
    a ``RequestContext``.
    """
    if hasattr(request, "_seo_metatags_loaded"):
        return {}

    setattr(request, "_seo_metatags_loaded", True)
    if not hasattr(request, "meta"):
        request.meta = {}

    try:
        tags = MetaTags.objects.get(url=normalize_url(request.path))
    except MetaTags.DoesNotExist:
        return {}

    request.meta.update(tags.seo_field_dict())
    return {}
