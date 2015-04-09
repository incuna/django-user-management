# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import user_management.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('date_joined', models.DateTimeField(editable=False, verbose_name='date joined', default=django.utils.timezone.now)),
                ('email', models.EmailField(unique=True, verbose_name='Email address', max_length=511)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('is_active', models.BooleanField(verbose_name='active', default=False)),
                ('email_verified', models.BooleanField(help_text='Indicates if the email address has been verified.', verbose_name='Email verified?', default=False)),
                ('avatar', models.ImageField(null=True, blank=True, upload_to='user_avatar')),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', blank=True, related_name='user_set', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', related_query_name='user', blank=True, related_name='user_set', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            bases=(user_management.models.mixins.EmailVerifyUserMethodsMixin, user_management.models.mixins.NameUserMethodsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BasicUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('date_joined', models.DateTimeField(editable=False, verbose_name='date joined', default=django.utils.timezone.now)),
                ('email', models.EmailField(unique=True, verbose_name='Email address', max_length=511)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(user_management.models.mixins.NameUserMethodsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CustomNameUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('date_joined', models.DateTimeField(editable=False, verbose_name='date joined', default=django.utils.timezone.now)),
                ('email', models.EmailField(unique=True, verbose_name='Email address', max_length=511)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(verbose_name='active', default=False)),
                ('email_verified', models.BooleanField(help_text='Indicates if the email address has been verified.', verbose_name='Email verified?', default=False)),
                ('avatar', models.ImageField(null=True, blank=True, upload_to='user_avatar')),
                ('name', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(user_management.models.mixins.EmailVerifyUserMethodsMixin, user_management.models.mixins.NameUserMethodsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CustomVerifyEmailUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('date_joined', models.DateTimeField(editable=False, verbose_name='date joined', default=django.utils.timezone.now)),
                ('email', models.EmailField(unique=True, verbose_name='Email address', max_length=511)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('is_active', models.BooleanField(verbose_name='active', default=False)),
                ('email_verified', models.BooleanField(help_text='Indicates if the email address has been verified.', verbose_name='Email verified?', default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(user_management.models.mixins.EmailVerifyUserMethodsMixin, user_management.models.mixins.NameUserMethodsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VerifyEmailUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('date_joined', models.DateTimeField(editable=False, verbose_name='date joined', default=django.utils.timezone.now)),
                ('email', models.EmailField(unique=True, verbose_name='Email address', max_length=511)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('is_active', models.BooleanField(verbose_name='active', default=False)),
                ('email_verified', models.BooleanField(help_text='Indicates if the email address has been verified.', verbose_name='Email verified?', default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(user_management.models.mixins.EmailVerifyUserMethodsMixin, user_management.models.mixins.NameUserMethodsMixin, models.Model),
        ),
    ]
