# Generated by Django 5.0.3 on 2024-03-15 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0005_alter_graph_employees_alter_graph_month_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetracking',
            name='worked_hours',
            field=models.CharField(default='0', max_length=5, null=True, verbose_name='Проработано часов'),
        ),
    ]