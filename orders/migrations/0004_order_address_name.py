# Generated by Django 3.2.4 on 2021-07-14 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
