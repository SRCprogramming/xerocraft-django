# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0018_auto_20160119_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paidmembership',
            name='ctrlid',
            field=models.CharField(null=True, help_text="Payment processor's id for this payment.", max_length=40),
        ),
    ]
