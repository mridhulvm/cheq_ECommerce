# Generated by Django 3.2.4 on 2021-07-13 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pin',
            field=models.IntegerField(blank=True, max_length=50, null=True),
        ),
    ]