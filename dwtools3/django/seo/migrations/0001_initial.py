# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dwtools3.django.helpers.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MetaTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('url', models.CharField(verbose_name='URL', unique=True, max_length=255)),
                ('title', dwtools3.django.helpers.fields.StrippedCharField(blank=True, max_length=255)),
                ('description', dwtools3.django.helpers.fields.StrippedTextField(blank=True)),
                ('keywords', dwtools3.django.helpers.fields.StrippedTextField(blank=True)),
                ('footer_text', dwtools3.django.helpers.fields.StrippedTextField(blank=True)),
            ],
            options={
                'verbose_name': 'meta tag',
                'verbose_name_plural': 'meta tags',
                'ordering': ('url',),
            },
        ),
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('url', models.CharField(verbose_name='URL', unique=True, max_length=255)),
                ('target_url', models.CharField(max_length=255)),
                ('is_permanent', models.BooleanField(help_text='Whether to use a 301 Permanent redirect for this entry.', default=False)),
                ('with_query_string', models.BooleanField(help_text='Whether to preserve any query string present in the source URL when redirecting.', default=False)),
            ],
            options={
                'verbose_name': 'redirect',
                'verbose_name_plural': 'redirects',
                'ordering': ('url',),
            },
        ),
    ]
