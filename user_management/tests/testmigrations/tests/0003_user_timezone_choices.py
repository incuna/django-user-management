# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytz
from django.db import migrations, models
from user_management.models.utils import timezone_choices


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_user_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='timezone',
            field=models.CharField(choices=timezone_choices(pytz.common_timezones), max_length=255),
        ),
    ]
