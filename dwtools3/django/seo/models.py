import re
from django.db import models
from ..helpers.fields import StrippedCharField, StrippedTextField


_PROTOCOL_DOMAIN_RE = re.compile(r'^[\w\-]+://[^/]+')


def normalize_url(url):
    url = url.strip()
    url = _PROTOCOL_DOMAIN_RE.sub('', url)

    try:
        url = url[:url.index('?')]
    except ValueError:
        pass

    try:
        url = url[:url.index('#')]
    except ValueError:
        pass

    url = url.rstrip('/')
    if url == '':
        url = '/'

    return url


def _clean_url_field(model, field):
    url = getattr(model, field)
    url = normalize_url(url)
    setattr(model, field, url)


class MetaTags(models.Model):
    url = models.CharField('URL', max_length=255, unique=True)
    title = StrippedCharField(max_length=255, blank=True)
    description = StrippedTextField(blank=True)
    keywords = StrippedTextField(blank=True)
    footer_text = StrippedTextField(blank=True)

    class Meta:
        ordering = ('url',)
        verbose_name = 'meta tag'
        verbose_name_plural = 'meta tags'

    def __str__(self):
        return self.url

    def clean(self):
        _clean_url_field(self, 'url')

    def seo_field_dict(self):
        return {f.name: getattr(self, f.name)
                for f in self._meta.get_fields()
                if f.name not in ('id', 'url') and getattr(self, f.name)}


class Redirect(models.Model):
    url = models.CharField('URL', max_length=255, unique=True)
    target_url = models.CharField(max_length=255, blank=False)
    is_permanent = models.BooleanField(default=False,
                                       help_text='Whether to use a 301 Permanent '
                                                 'redirect for this entry.')
    with_query_string = models.BooleanField(default=False,
                                            help_text='Whether to preserve any query string '
                                                      'present in the source URL when redirecting.')

    class Meta:
        ordering = ('url',)
        verbose_name = 'redirect'
        verbose_name_plural = 'redirects'

    def __str__(self):
        return '{} -> {}'.format(self.url, self.target_url)

    def clean(self):
        _clean_url_field(self, 'url')
        if self.with_query_string:
            _clean_url_field(self, 'target_url')
