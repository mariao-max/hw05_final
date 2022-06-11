# Generated by Django 2.2.16 on 2022-06-11 07:44

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20211214_1411'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='no yourself follow',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, user=django.db.models.expressions.F('author')), name='no_yourself_follow'),
        ),
    ]