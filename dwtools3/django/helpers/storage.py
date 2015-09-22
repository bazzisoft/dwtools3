"""
Additional storage backend for overwriting files with the same name.

Usage
-----
::

from dwtools3.django.helpers.storage import OverwriteStorage

class Media(models.Model):
    name = models.CharField(max_length=128))
    media = models.FileField(upload_to=settings.MEDIA_DIR, storage=OverwriteStorage())
"""
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    """
    File-system storage backend that overwrites files with the same name.
    """
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
