# Generated by Django 3.2.4 on 2021-07-16 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_category_offer_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='offer_percentage',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
