# Generated by Django 5.0.3 on 2024-06-01 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0010_graph_cms_graph_graph_json_alter_graph_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graph',
            name='graph_json',
            field=models.TextField(null=True, verbose_name='base64 json Графика'),
        ),
    ]