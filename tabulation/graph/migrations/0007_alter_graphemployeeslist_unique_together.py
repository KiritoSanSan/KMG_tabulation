# Generated by Django 5.0.3 on 2024-05-16 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0006_alter_graphemployeeslist_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='graphemployeeslist',
            unique_together={('employee_id', 'graph_id')},
        ),
    ]
