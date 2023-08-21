# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SyncQueueItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, primary_key=True, auto_created=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("scheduled_at", models.DateTimeField(blank=True, db_index=True)),
                (
                    "reschedule_on_error",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="If task fails, reschedule it after this many minutes",
                        null=True,
                    ),
                ),
                ("module", models.CharField(max_length=255)),
                ("function", models.CharField(max_length=128)),
                ("_params", models.TextField(blank=True)),
            ],
            options={
                "ordering": ("scheduled_at",),
            },
        ),
    ]
