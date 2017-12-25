"""
Additional storage backends for static files and media.

Usage
-----
::

# OverwriteStorage
from dwtools3.django.helpers.storage import OverwriteStorage

class Media(models.Model):
    name = models.CharField(max_length=128))
    media = models.FileField(upload_to=settings.MEDIA_DIR, storage=OverwriteStorage())


# NonStrictManifestStaticFilesStorage
STATICFILES_STORAGE = 'dwtools3.django.helpers.storage.NonStrictManifestStaticFilesStorage'


# Lazy version of staticfiles `static()`
from dwtools3.django.helpers.storage import static_lazy
lazy_url_str = static_lazy('my_url_name')

"""
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.files.storage import FileSystemStorage
from django.templatetags.static import static
from django.utils.functional import lazy


class OverwriteStorage(FileSystemStorage):
    """
    File-system storage backend that overwrites files with the same name.
    """
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name


class NonStrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False


static_lazy = lazy(static, str)
