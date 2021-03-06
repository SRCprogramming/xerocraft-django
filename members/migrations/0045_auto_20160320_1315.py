# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0044_groupmembership_sale_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='family_count',
        ),
        migrations.AlterField(
            model_name='membership',
            name='membership_type',
            field=models.CharField(choices=[('R', 'Regular'), ('W', 'Work-Trade'), ('S', 'Scholarship'), ('C', 'Complimentary'), ('G', 'Group'), ('F', 'Family')], help_text='The type of membership.', default='R', max_length=1),
        ),
    ]
