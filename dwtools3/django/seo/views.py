from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from .models import MetaTags


def seo_metatags_admin_redirect(request):
    url = request.GET.get('url', None)
    if not url:
        raise ValueError('No URL was provided in SEO redirect request.')

    try:
        metatags = MetaTags.objects.get(url=url)
        return redirect('admin:seo_metatags_change', metatags.id)
    except MetaTags.DoesNotExist:
        return redirect(reverse('admin:seo_metatags_add') + '?url=' + urlquote(url))
