# Generated by Django 3.2.4 on 2021-07-21 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral', '0007_referralusers_referral_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referral',
            name='is_available',
        ),
        migrations.RemoveField(
            model_name='referral',
            name='referral_count',
        ),
        migrations.AddField(
            model_name='referral',
            name='is_ordered_recommended_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='referral',
            name='is_ordered_user',
            field=models.BooleanField(default=False),
        ),
    ]
