# Generated by Django 2.2.16 on 2021-12-14 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20211214_1359'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='no yourself follow',
        ),
    ]