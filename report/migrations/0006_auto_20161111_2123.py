# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-11 21:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0005_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='formatter_url',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]