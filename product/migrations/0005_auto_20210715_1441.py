# Generated by Django 3.2.4 on 2021-07-15 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_rename_images_product_image1'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='offer_percentage',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='offer_price',
            field=models.IntegerField(null=True),
        ),
    ]
