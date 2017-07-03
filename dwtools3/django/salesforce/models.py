import json
import decimal
from django.utils import timezone
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder


class DecimalDjangoJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        return super(DecimalDjangoJSONEncoder, self).default(o)


class SyncQueueItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(db_index=True, blank=True)
    reschedule_on_error = models.PositiveIntegerField(
        blank=True, null=True,
        help_text='If task fails, reschedule it after this many minutes')
    module = models.CharField(max_length=255)
    function = models.CharField(max_length=128)
    _params = models.TextField(blank=True)

    class Meta:
        ordering = ('scheduled_at',)

    def __str__(self):
        return '<SyncQueueItem id={} function={}>'.format(self.id, self.function)

    def save(self, *args, **kwargs):
        if not self.scheduled_at:
            self.scheduled_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def params(self):
        return json.loads(self._params)

    @params.setter
    def params(self, value):
        self._params = json.dumps(value, cls=DecimalDjangoJSONEncoder)
