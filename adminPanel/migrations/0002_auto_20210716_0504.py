# Generated by Django 3.2.4 on 2021-07-16 05:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminPanel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productoffer',
            name='product',
        ),
        migrations.DeleteModel(
            name='CategoryOffer',
        ),
        migrations.DeleteModel(
            name='ProductOffer',
        ),
    ]
