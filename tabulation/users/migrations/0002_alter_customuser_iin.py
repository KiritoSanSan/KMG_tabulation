# Generated by Django 5.0.3 on 2024-05-15 04:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='iin',
            field=models.CharField(max_length=12, unique=True, validators=[django.core.validators.MinLengthValidator(12, 'Не правильный ИИН')], verbose_name='ИИН'),
        ),
    ]
