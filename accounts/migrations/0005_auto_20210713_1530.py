# Generated by Django 3.2.4 on 2021-07-13 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_useraddress_address_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='phone',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='pin',
            field=models.CharField(max_length=6),
        ),
    ]
