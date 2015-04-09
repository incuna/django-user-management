# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import user_management.api.models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('key', models.CharField(primary_key=True, serialize=False, max_length=40)),
                ('created', models.DateTimeField(editable=False, default=django.utils.timezone.now)),
                ('expires', models.DateTimeField(editable=False, default=user_management.api.models.update_expiry)),
            ],
        ),
    ]
