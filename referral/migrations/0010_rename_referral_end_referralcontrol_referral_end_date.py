# Generated by Django 3.2.4 on 2021-07-22 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0009_auto_20210722_0233'),
    ]

    operations = [
        migrations.RenameField(
            model_name='referralcontrol',
            old_name='referral_end',
            new_name='referral_end_date',
        ),
    ]