# Generated by Django 5.0.7 on 2024-08-16 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OilTraders', '0004_newentry_ac_filter_newentry_air_filter_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='newentry',
            name='oil_filter',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
