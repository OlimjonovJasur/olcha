# Generated by Django 5.1.7 on 2025-04-08 06:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('olcha', '0006_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
    ]
