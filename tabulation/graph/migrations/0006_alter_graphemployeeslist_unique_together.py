# Generated by Django 5.0.3 on 2024-05-16 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0005_alter_timetracking_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='graphemployeeslist',
            unique_together=set(),
        ),
    ]
