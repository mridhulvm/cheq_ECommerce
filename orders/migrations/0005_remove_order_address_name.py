# Generated by Django 3.2.4 on 2021-07-14 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_address_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='address_name',
        ),
    ]
