# Generated by Django 3.2.4 on 2021-07-16 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_productoffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='productoffer',
            name='offer_price',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productoffer',
            name='offer',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]